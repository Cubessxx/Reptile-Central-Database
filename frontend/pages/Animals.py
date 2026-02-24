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

page_setup(title="Animals", icon="🐍", page_heading="Animals")

tab_browse, tab_create, tab_update, tab_delete = st.tabs(
    ["Browse Animals", "Create Animal", "Update Animal", "Delete Animal"]
)

#Browse Animals Tab
render_browse_tab(
    tab=tab_browse,
    name="Browse Animals",
    view="v_browse_animals_page",
)

#Create Animal Tab
ANIMAL_CREATE_SPECS = [
    {"label": "Name",    "type": "text"},
    {"label": "Species", "type": "text"},
    {"label": "Age",     "type": "int",     "min": 0,   "step": 1,    "default": 0},
    {"label": "Price",   "type": "decimal", "min": 0.0, "step": 0.01, "default": 0.0},
]

render_create_tab(
    tab=tab_create,
    name="Create Animal",
    create_id="Animal",
    specs=ANIMAL_CREATE_SPECS,
    form_key="create_animal_form",
    submit_label="Create Animal",
)

#Update Animal Tab
ANIMAL_UPDATE_SPECS = [
    {"label": "Age",       "type": "int",     "source": "Age",       "min": 0,   "step": 1,    "default": 0},
    {"label": "Price",     "type": "decimal", "source": "Price",     "min": 0.0, "step": 0.01, "default": 0.0},
    {"label": "Available", "type": "select",  "source": "Available", "options": ["Yes", "No"]},
]

render_update_tab(
    tab=tab_update,
    name="Update Animal",
    view="v_browse_animals_page",
    update_id="Animal",
    target_id="Animal ID",
    label_field_1="Name",
    specs=ANIMAL_UPDATE_SPECS,
    form_key="update_animal_form",
    submit_label="Update Animal",
)

#Delete Animal Tab
render_delete_tab(
    tab=tab_delete,
    name="Delete Animal",
    view="v_browse_animals_page",
    delete_id="Animal ID",
    label_field_1="Name",
)
