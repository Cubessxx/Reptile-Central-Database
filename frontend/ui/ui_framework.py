#
# Citation for use of AI Tools:
# Date: 02/23/2026
# Prompts used to generate Python/Streamlit code
# We originally wrote each page by hand with repeated boilerplate for browse/create/update/delete tabs.
# With many iterative prompts, AI helped us design a reusable shared ui_framework.py to unify common page logic.
# AI Source URL: https://chat.openai.com/
#

import pandas as pd
import streamlit as st
from backend.db import get_engine
from frontend.ui.reset_button import render_reset_button
from sqlalchemy import text


# Page Setup
def page_setup(title: str, icon: str, page_heading: str = None) -> None:
    """Configure a Streamlit page and render the reset database button."""
    st.set_page_config(page_title=title, page_icon=icon, layout="wide")
    render_reset_button(key="reset_db_button")

    if page_heading:
        st.title(page_heading)


# Shared Helpers
def normalize_text(val: str) -> str | None:
    """Take in a string and return NULL if it is the empty string(""). This is helpful so that a unaltered form submission box does not pass NOT NULL constraints"""
    val = val.strip()
    return val or None


def build_display_labels(df: pd.DataFrame, label_fields: list[str]) -> pd.Series:
    """Build dropdown labels for Selectbox submissions"""
    if not label_fields:
        raise ValueError("At least one label field is required.")

    missing = [field for field in label_fields if field not in df.columns]
    if missing:
        raise ValueError(f"Missing label fields in view data: {missing}")

    label_parts = [df[field].fillna("").astype(str).str.strip() for field in label_fields]
    display = label_parts[0]
    for part in label_parts[1:]:
        display = (display + " " + part).str.strip()

    return display.str.replace(r"\s+", " ", regex=True).str.strip()


def select_default_index(options: list, source_val: object, fallback: int = 0) -> int:
    """Find the best default option index by exact match, then string match."""
    if source_val in options:
        return options.index(source_val)
    return fallback


def resolve_select_value(selected_option: object, value_map: object) -> object:
    """Map a selected option to a stored value when value_map is provided."""
    return selected_option


def format_select_option(spec: dict):
    """Return a safe format function for select widgets."""
    return spec.get("format_func") or (lambda option: option)


def render_missing_select_options(label: str, spec: dict) -> None:
    """Render a user-facing message when a select field has no options."""
    st.write(spec.get("empty_options_message", f"No options available for {label}."))


# Tab Renderers
def render_browse_tab(tab, name: str, view: str) -> None:
    """Render a browse tab from a database view."""
    with tab:
        st.subheader(name)
        engine = get_engine()
        df = pd.read_sql(f"SELECT * FROM {view};", engine)
        st.dataframe(df, width="stretch", hide_index=True)


def render_delete_tab(
    tab,
    name: str,
    view: str,
    delete_id: str,
    label_field_1: str,
    label_field_2: str = None,
    label_field_3: str = None,
) -> None:
    """Render a generic delete tab powered by sp_generic_delete."""
    with tab:
        st.subheader(name)
        engine = get_engine()
        df = pd.read_sql(f"SELECT * FROM {view};", engine)

        if df.empty:
            st.write("No records to delete.")
            return

        if delete_id not in df.columns:
            raise ValueError(f"Delete id column '{delete_id}' not found in view '{view}'.")

        label_fields = [field for field in [label_field_1, label_field_2, label_field_3] if field]
        df = df.copy()
        df["_display_label"] = build_display_labels(df, label_fields)
        options = df.index.tolist()

        selected_idx = st.selectbox(
            "Select Record",
            options,
            format_func=lambda i: df.loc[i, "_display_label"],
        )
        selected_id = df.loc[selected_idx, delete_id]

        if st.button("Delete"):
            with engine.begin() as conn:
                conn.execute(
                    text(
                        """
                        CALL sp_generic_delete(
                            :delete_id,
                            :target_id
                        );
                        """
                    ),
                    {
                        "delete_id": delete_id,
                        "target_id": str(selected_id),
                    },
                )
            st.rerun()


def render_update_tab(
    tab,
    name: str,
    view: str,
    update_id: str,
    target_id: str,
    label_field_1: str,
    label_field_2: str = None,
    label_field_3: str = None,
    specs: list[dict] | None = None,
    form_key: str = "update_form",
    submit_label: str = "Update",
) -> None:
    """Render a generic update tab powered by sp_generic_update with up to four inputs."""
    specs = specs or []
    if len(specs) > 4:
        raise ValueError("render_update_tab supports at most 4 fields (p1..p4).")

    with tab:
        st.subheader(name)
        engine = get_engine()
        df = pd.read_sql(f"SELECT * FROM {view};", engine)

        if df.empty:
            st.write("No records to update.")
            return

        if target_id not in df.columns:
            raise ValueError(f"Target id column '{target_id}' not found in view '{view}'.")

        label_fields = [field for field in [label_field_1, label_field_2, label_field_3] if field]
        df = df.copy()
        df["_display_label"] = build_display_labels(df, label_fields)
        options = df.index.tolist()

        selected_idx = st.selectbox(
            "Select Record",
            options,
            format_func=lambda i: df.loc[i, "_display_label"],
            key=f"{form_key}_record_selector",
        )
        row = df.loc[selected_idx]
        selected_target_id = row[target_id]

        with st.form(form_key):
            p = {"p1": None, "p2": None, "p3": None, "p4": None}

            for idx, s in enumerate(specs):
                param = f"p{idx + 1}"
                label = s["label"]
                ftype = s["type"]
                source_col = s.get("source")

                if source_col and source_col not in df.columns:
                    raise ValueError(f"Source column '{source_col}' not found in view '{view}'.")

                source_val = row[source_col] if source_col else None

                if ftype == "text":
                    raw = st.text_input(
                        label,
                        value="" if pd.isna(source_val) else str(source_val),
                        placeholder=s.get("placeholder"),
                        help=s.get("help"),
                    )
                    p[param] = normalize_text(raw)

                elif ftype == "int":
                    default_val = int(source_val)
                    num = st.number_input(
                        label,
                        min_value=s.get("min", None),
                        max_value=s.get("max", None),
                        value=default_val,
                        step=s.get("step", 1),
                        help=s.get("help"),
                    )
                    p[param] = int(num)

                elif ftype == "decimal":
                    default_val = float(source_val)
                    num = st.number_input(
                        label,
                        min_value=s.get("min", None),
                        max_value=s.get("max", None),
                        value=default_val,
                        step=s.get("step", 0.01),
                        help=s.get("help"),
                    )
                    p[param] = float(num)

                elif ftype == "select":
                    option_list = s.get("options", [])
                    if not option_list:
                        render_missing_select_options(label, s)
                        return

                    default_index = select_default_index(option_list, source_val)
                    selected_option = st.selectbox(
                        label,
                        option_list,
                        index=default_index,
                        format_func=format_select_option(s),
                        help=s.get("help"),
                    )
                    p[param] = resolve_select_value(selected_option, s.get("value_map"))

                else:
                    raise ValueError(f"Unsupported type '{ftype}' for '{label}'")

            submitted = st.form_submit_button(submit_label)

        if submitted:
            with engine.begin() as conn:
                conn.execute(
                    text("CALL sp_generic_update(:update_id, :target_id, :p1, :p2, :p3, :p4);"),
                    {"update_id": update_id, "target_id": str(selected_target_id), **p},
                )
            st.rerun()


def render_create_tab(
    tab,
    name: str,
    create_id: str,
    specs: list[dict],
    form_key: str,
    submit_label: str,
) -> None:
    """Render a generic create tab powered by sp_generic_create with up to four inputs."""
    if len(specs) > 4:
        raise ValueError("render_create_tab supports at most 4 fields (p1..p4).")

    with tab:
        st.subheader(name)
        engine = get_engine()

        with st.form(form_key, clear_on_submit=True):
            p = {"p1": None, "p2": None, "p3": None, "p4": None}

            for idx, s in enumerate(specs):
                param = f"p{idx + 1}"
                label = s["label"]
                ftype = s["type"]

                if ftype == "text":
                    raw = st.text_input(
                        label,
                        placeholder=s.get("placeholder"),
                        help=s.get("help"),
                    )
                    p[param] = normalize_text(raw)

                elif ftype == "int":
                    num = st.number_input(
                        label,
                        min_value=s.get("min", None),
                        max_value=s.get("max", None),
                        value=s.get("default", 0),
                        step=s.get("step", 1),
                        help=s.get("help"),
                    )
                    p[param] = int(num)

                elif ftype == "decimal":
                    num = st.number_input(
                        label,
                        min_value=s.get("min", None),
                        max_value=s.get("max", None),
                        value=s.get("default", 0.0),
                        step=s.get("step", 0.01),
                        help=s.get("help"),
                    )
                    p[param] = float(num)

                elif ftype == "select":
                    option_list = s.get("options", [])
                    if not option_list:
                        render_missing_select_options(label, s)
                        return

                    default_index = select_default_index(option_list, s.get("default"))
                    selected_option = st.selectbox(
                        label,
                        option_list,
                        index=default_index,
                        format_func=format_select_option(s),
                        help=s.get("help"),
                    )
                    p[param] = resolve_select_value(selected_option, s.get("value_map"))

                else:
                    raise ValueError(f"Unsupported type '{ftype}' for '{label}'")

            submitted = st.form_submit_button(submit_label)

        if submitted:
            with engine.begin() as conn:
                conn.execute(
                    text("CALL sp_generic_create(:create_id, :p1, :p2, :p3, :p4);"),
                    {"create_id": create_id, **p},
                )
            st.rerun()
