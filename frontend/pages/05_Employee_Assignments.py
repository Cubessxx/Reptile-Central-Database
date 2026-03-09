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


page_setup(title="Employee Assignments", icon="🔗", page_heading="Employee Assignments")
engine = get_engine()

animals_df = pd.read_sql("SELECT * FROM v_browse_animals_page;", engine)
employees_df = pd.read_sql("SELECT * FROM v_browse_employees_page;", engine)

animal_options = animals_df["Animal ID"].astype(int).tolist()
employee_create_options = employees_df["Employee ID"].astype(int).tolist()
employee_update_options = [None] + employee_create_options

animal_lookup = {
    int(row["Animal ID"]): f'{int(row["Animal ID"])} - {row["Name"]} ({row["Species"]})'
    for _, row in animals_df.iterrows()
}

employee_lookup = {None: "Unassigned"}
employee_lookup.update(
    {
        int(row["Employee ID"]): f'{int(row["Employee ID"])} - {row["First Name"]} {row["Last Name"]}'
        for _, row in employees_df.iterrows()
    }
)


def format_animal_option(animal_id):
    return animal_lookup.get(animal_id, str(animal_id))


def format_employee_option(employee_id):
    return employee_lookup.get(employee_id, str(employee_id))


ASSIGNMENT_CREATE_SPECS = [
    {
        "label": "Animal",
        "type": "select",
        "options": animal_options,
        "format_func": format_animal_option,
        "empty_options_message": "No animals found. Use the Animals page first.",
    },
    {
        "label": "Employee",
        "type": "select",
        "options": employee_create_options,
        "format_func": format_employee_option,
    },
]

ASSIGNMENT_UPDATE_SPECS = [
    {
        "label": "Animal",
        "type": "select",
        "source": "Animal ID",
        "options": animal_options,
        "format_func": format_animal_option,
        "empty_options_message": "No animals found. Use the Animals page first.",
    },
    {
        "label": "Employee",
        "type": "select",
        "source": "Employee ID",
        "options": employee_update_options,
        "format_func": format_employee_option,
    },
]

tab_browse, tab_create, tab_update, tab_delete = st.tabs(
    ["Browse Assignments", "Create Assignment", "Update Assignment", "Delete Assignment"]
)

#Browse Assignments Tab
render_browse_tab(
    tab=tab_browse,
    name="Browse Assignments",
    view="v_browse_employee_assignments_page",
)

#Create Assignment Tab
render_create_tab(
    tab=tab_create,
    name="Create Assignment",
    create_id="Employee Assignment",
    specs=ASSIGNMENT_CREATE_SPECS,
    form_key="create_employee_assignment_form",
    submit_label="Create Assignment",
)

#Update Assignment Tab
render_update_tab(
    tab=tab_update,
    name="Update Assignment",
    view="v_browse_employee_assignments_page",
    update_id="Employee Assignment",
    target_id="Assignment ID",
    label_field_1="Assignment ID",
    label_field_2="Animal Name",
    label_field_3="Employee Last Name",
    specs=ASSIGNMENT_UPDATE_SPECS,
    form_key="update_employee_assignment_form",
    submit_label="Update Assignment",
)

#Delete Assignment Tab
render_delete_tab(
    tab=tab_delete,
    name="Delete Assignment",
    view="v_browse_employee_assignments_page",
    delete_id="Assignment ID",
    label_field_1="Assignment ID",
    label_field_2="Animal Name",
    label_field_3="Employee Last Name",
)
