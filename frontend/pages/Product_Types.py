from pathlib import Path
import sys

for parent in Path(__file__).resolve().parents:
    if (parent / "frontend").is_dir() and (parent / "backend").is_dir():
        parent_str = str(parent)
        if parent_str not in sys.path:
            sys.path.insert(0, parent_str)
        break

import streamlit as st
from frontend.ui.ui_framework import (
    page_setup,
    render_browse_tab,
    render_create_tab,
    render_update_tab,
    render_delete_tab,
)

page_setup(title="Product Types", icon="🏷️", page_heading="Product Types")

tab_browse, tab_create, tab_update, tab_delete = st.tabs(
    ["Browse Product Types", "Create Product Type", "Update Product Type", "Delete Product Type"]
)

#Browse Product Types Tab
render_browse_tab(
    tab=tab_browse,
    name="Browse Product Types",
    view="v_browse_product_types_page",
)

#Create Product Type Tab
PRODUCT_TYPE_CREATE_SPECS = [
    {"label": "Product Type Code", "type": "text"},
    {"label": "Product Type Name", "type": "text"},
]

render_create_tab(
    tab=tab_create,
    name="Create Product Type",
    create_id="Product Type",
    specs=PRODUCT_TYPE_CREATE_SPECS,
    form_key="create_product_type_form",
    submit_label="Create Product Type",
)

#Update Product Type Tab
PRODUCT_TYPE_UPDATE_SPECS = [
    {"label": "Product Type Name", "type": "text", "source": "Product Type Name"},
]

render_update_tab(
    tab=tab_update,
    name="Update Product Type",
    view="v_browse_product_types_page",
    update_id="Product Type",
    target_id="Product Type Code",
    label_field_1="Product Type Code",
    label_field_2="Product Type Name",
    specs=PRODUCT_TYPE_UPDATE_SPECS,
    form_key="update_product_type_form",
    submit_label="Update Product Type",
)

#Delete Product Type Tab
render_delete_tab(
    tab=tab_delete,
    name="Delete Product Type",
    view="v_browse_product_types_page",
    delete_id="Product Type Code",
    label_field_1="Product Type Code",
    label_field_2="Product Type Name",
)
