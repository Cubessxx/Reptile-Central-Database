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

page_setup(title="Customers", icon="🙋🏻‍♂️", page_heading="Customers")

tab_browse, tab_create, tab_update, tab_delete = st.tabs(
    ["Browse Customers", "Create Customer", "Update Customer", "Delete Customer"]
)

#Browse Customers Tab
render_browse_tab(
    tab=tab_browse,
    name="Browse Customers",
    view="v_browse_customers_page",
)

#Create Customer Tab
CUSTOMER_CREATE_SPECS = [
    {"label": "First Name",   "type": "text"},
    {"label": "Last Name",    "type": "text"},
    {"label": "Email",        "type": "text"},
    {"label": "Phone Number", "type": "text"},
]

render_create_tab(
    tab=tab_create,
    name="Create Customer",
    create_id="Customer",
    specs=CUSTOMER_CREATE_SPECS,
    form_key="create_customer_form",
    submit_label="Create Customer",
)

#Update Customer Tab
CUSTOMER_UPDATE_SPECS = [
    {"label": "Email",        "type": "text", "source": "Email"},
    {"label": "Phone Number", "type": "text", "source": "Phone Number"},
]

render_update_tab(
    tab=tab_update,
    name="Update Customer",
    view="v_browse_customers_page",
    update_id="Customer",
    target_id="Customer ID",
    label_field_1="First Name",
    label_field_2="Last Name",
    specs=CUSTOMER_UPDATE_SPECS,
    form_key="update_customer_form",
    submit_label="Update Customer",
)

#Delete Customer Tab
render_delete_tab(
    tab=tab_delete,
    name="Delete Customer",
    view="v_browse_customers_page",
    delete_id="Customer ID",
    label_field_1="First Name",
    label_field_2="Last Name",
)
