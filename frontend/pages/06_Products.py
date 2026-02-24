import pandas as pd
import streamlit as st

from backend.db import get_engine
from frontend.ui.ui_framework import (
    page_setup,
    render_browse_tab,
    render_create_tab,
    render_update_tab,
    render_delete_tab,
)


page_setup(title="Products", icon="📦", page_heading="Products")
engine = get_engine()

tab_browse, tab_create, tab_update, tab_delete = st.tabs(
    ["Browse Products", "Create Product", "Update Product", "Delete Product"]
)

#Browse Products Tab
render_browse_tab(
    tab=tab_browse,
    name="Browse Products",
    view="v_browse_products_page",
)

product_types_df = pd.read_sql("SELECT * FROM v_browse_product_types_page;", engine)
type_code_options = product_types_df["Product Type Code"].astype(str).tolist()
type_name_lookup = dict(
    zip(
        product_types_df["Product Type Code"].astype(str),
        product_types_df["Product Type Name"].astype(str),
    )
)


def format_product_type(code: str) -> str:
    return f"{code} - {type_name_lookup.get(str(code), '')}"


PRODUCT_CREATE_SPECS = [
    {"label": "Product Name", "type": "text"},
    {
        "label": "Product Type",
        "type": "select",
        "options": type_code_options,
        "format_func": format_product_type,
        "empty_options_message": "No product types found. Use the Product Types page first.",
    },
    {"label": "Price", "type": "decimal", "min": 0.0, "step": 0.01, "default": 0.0},
    {"label": "Stock", "type": "int", "min": 0, "step": 1, "default": 0},
]

PRODUCT_UPDATE_SPECS = [
    {"label": "Product Name", "type": "text", "source": "Product Name"},
    {
        "label": "Product Type",
        "type": "select",
        "source": "Product Type Code",
        "options": type_code_options,
        "format_func": format_product_type,
        "empty_options_message": "No product types found. Use the Product Types page first.",
    },
    {"label": "Price", "type": "decimal", "source": "Price", "min": 0.0, "step": 0.01, "default": 0.0},
    {"label": "Stock", "type": "int", "source": "Stock", "min": 0, "step": 1, "default": 0},
]

#Create Product Tab
render_create_tab(
    tab=tab_create,
    name="Create Product",
    create_id="Product",
    specs=PRODUCT_CREATE_SPECS,
    form_key="create_product_form",
    submit_label="Create Product",
)

#Update Product Tab
render_update_tab(
    tab=tab_update,
    name="Update Product",
    view="v_browse_products_page",
    update_id="Product",
    target_id="Product ID",
    label_field_1="Product Name",
    specs=PRODUCT_UPDATE_SPECS,
    form_key="update_product_form",
    submit_label="Update Product",
)

#Delete Product Tab
render_delete_tab(
    tab=tab_delete,
    name="Delete Product",
    view="v_browse_products_page",
    delete_id="Product ID",
    label_field_1="Product Name",
)
