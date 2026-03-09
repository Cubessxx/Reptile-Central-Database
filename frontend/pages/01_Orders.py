import time

import pandas as pd
import streamlit as st
from sqlalchemy import text

from backend.db import get_engine
from frontend.ui.ui_framework import (
    page_setup,
    queue_success_message,
    render_browse_tab,
    render_delete_tab,
    render_success_message,
)


ORDER_DETAILS_QUERY = text(
    "SELECT * FROM v_browse_order_details_page "
    "WHERE `Order ID` = :order_id "
    "ORDER BY `Order Details ID`;"
)
CREATE_ORDER_QUERY = text("CALL sp_generic_create(:create_id, :p1, :p2, :p3, :p4);")
UPSERT_ORDER_DETAIL_QUERY = text(
    "CALL sp_generic_update(:update_id, :target_id, :p1, :p2, :p3, :p4);"
)
CREATE_ORDER_SUCCESS_KEY = "orders_create_success"
UPDATE_ORDER_ITEM_SUCCESS_KEY = "orders_update_item_success"
CREATE_ORDER_PRODUCTS_EDITOR_KEY_PREFIX = "create_order_products_editor"
CREATE_ORDER_PRODUCTS_EDITOR_VERSION_KEY = "create_order_products_editor_version"
ORDER_SUCCESS_MESSAGE_DURATION_SECONDS = 3


def full_name(df: pd.DataFrame, first_col: str, last_col: str) -> pd.Series:
    """Join first and last name columns into one label."""
    return (
        df[first_col].fillna("").astype(str).str.strip()
        + " "
        + df[last_col].fillna("").astype(str).str.strip()
    ).str.replace(r"\s+", " ", regex=True).str.strip()


def id_label_map(df: pd.DataFrame, id_col: str, label_col: str) -> dict[int, str]:
    """Make a dictionary of ids to labels for selectboxes."""
    return dict(zip(df[id_col].astype(int), df[label_col].astype(str)))


def load_page_data(engine):
    """Load the data used by the Orders page."""
    orders_df = pd.read_sql("SELECT * FROM v_browse_orders_page;", engine)
    customers_df = pd.read_sql("SELECT * FROM v_browse_customers_page;", engine)
    employees_df = pd.read_sql("SELECT * FROM v_browse_employees_page;", engine)
    products_df = pd.read_sql("SELECT * FROM v_browse_products_page;", engine)

    customers_df["Customer Name"] = full_name(customers_df, "First Name", "Last Name")
    employees_df["Employee Name"] = full_name(employees_df, "First Name", "Last Name")
    orders_df["Customer Name"] = full_name(orders_df, "First Name", "Last Name")

    return orders_df, customers_df, employees_df, products_df


def create_order_header(conn, customer_id: int, employee_id: int) -> int:
    """Create a new order and return its ID."""
    row = conn.execute(
        CREATE_ORDER_QUERY,
        {
            "create_id": "Order",
            "p1": customer_id,
            "p2": employee_id,
            "p3": None,
            "p4": None,
        },
    ).fetchone()
    return int(row[0])


def upsert_order_item(conn, order_id: int, product_id: int, qty: int) -> None:
    """Add or update an item in an order."""
    conn.execute(
        UPSERT_ORDER_DETAIL_QUERY,
        {
            "update_id": "Order Detail",
            "target_id": order_id,
            "p1": product_id,
            "p2": qty,
            "p3": None,
            "p4": None,
        },
    )


def render_create_order_tab(tab, engine, customers_df, employees_df, products_df) -> None:
    """Show the Create Order tab."""
    with tab:
        st.subheader("Create Order")
        st.write("Create a new order in the system with a selected customer and assigned employee.")

        customer_options = id_label_map(customers_df, "Customer ID", "Customer Name")
        employee_options = id_label_map(employees_df, "Employee ID", "Employee Name")
        editor_version = int(st.session_state.get(CREATE_ORDER_PRODUCTS_EDITOR_VERSION_KEY, 0))
        editor_key = f"{CREATE_ORDER_PRODUCTS_EDITOR_KEY_PREFIX}_{editor_version}"

        entry_df = products_df[["Product ID", "Product Name", "Price"]].copy()
        entry_df.rename(columns={"Price": "Unit Price"}, inplace=True)
        entry_df["Quantity"] = 0

        with st.form("create_order_form"):
            customer_id = st.selectbox(
                "Customer",
                list(customer_options),
                format_func=customer_options.get,
                key="create_order_customer",
            )
            employee_id = st.selectbox(
                "Assigned Employee",
                list(employee_options),
                format_func=employee_options.get,
                key="create_order_employee",
            )
            st.caption("Set quantities for products included in the order.")
            edited_df = st.data_editor(
                entry_df,
                width="stretch",
                hide_index=True,
                disabled=["Product ID", "Product Name", "Unit Price"],
                column_config={
                    "Quantity": st.column_config.NumberColumn("Quantity", min_value=0, step=1)
                },
                key=editor_key,
            )
            submitted = st.form_submit_button("Create Order")

        if submitted:
            items = edited_df.query("Quantity > 0")[["Product ID", "Quantity"]].astype(int)
            if items.empty:
                message_placeholder = st.empty()
                message_placeholder.error("A order must contain atleast one item.")
                time.sleep(3)
                message_placeholder.empty()
                return

            with engine.begin() as conn:
                new_order_id = create_order_header(conn, int(customer_id), int(employee_id))
                for product_id, qty in items.itertuples(index=False, name=None):
                    upsert_order_item(conn, new_order_id, int(product_id), int(qty))
            st.session_state[CREATE_ORDER_PRODUCTS_EDITOR_VERSION_KEY] = editor_version + 1
            queue_success_message(CREATE_ORDER_SUCCESS_KEY, "Order created successfully.")
            st.rerun()

        render_success_message(CREATE_ORDER_SUCCESS_KEY, ORDER_SUCCESS_MESSAGE_DURATION_SECONDS)


def render_details_tab(tab, engine, orders_df, products_df) -> None:
    """Show the order details tab for viewing and editing items."""
    with tab:
        render_success_message(
            UPDATE_ORDER_ITEM_SUCCESS_KEY,
            ORDER_SUCCESS_MESSAGE_DURATION_SECONDS,
        )
        if orders_df.empty:
            st.write("No orders found.")
            return

        st.write("Select an order to view or edit.")
        order_options = {
            int(order_id): f"Order ID: {int(order_id)} Name: {customer_name}"
            for order_id, customer_name in orders_df[["Order ID", "Customer Name"]].itertuples(
                index=False, name=None
            )
        }
        order_id = st.selectbox(
            "Order",
            list(order_options),
            format_func=order_options.get,
            key="update_order_select",
        )

        details_df = pd.read_sql(ORDER_DETAILS_QUERY, engine, params={"order_id": int(order_id)})
        if details_df.empty:
            st.write("No line items for this order.")
        else:
            st.dataframe(details_df, width="stretch", hide_index=True)

        st.divider()
        st.subheader("Update or Add Items")
        st.write("Select an item to add or update in the order.")

        product_options = id_label_map(products_df, "Product ID", "Product Name")
        product_id = st.selectbox(
            "Select Item",
            list(product_options),
            format_func=product_options.get,
            key="update_or_add_item_select",
        )
        qty = st.number_input(
            "Quantity",
            min_value=1,
            step=1,
            value=1,
            key="update_or_add_item_qty",
        )

        if st.button("Update or Add Item"):
            with engine.begin() as conn:
                upsert_order_item(conn, int(order_id), int(product_id), int(qty))
            queue_success_message(UPDATE_ORDER_ITEM_SUCCESS_KEY, "Order item updated successfully.")
            st.rerun()


page_setup(title="Orders", icon="📄", page_heading="Orders")
engine = get_engine()
orders_df, customers_df, employees_df, products_df = load_page_data(engine)

tab_browse, tab_create_order, tab_update_details, tab_delete = st.tabs(
    ["Order Overview", "Create Order", "View or Update Order Details", "Delete Order"]
)

#Order Overview Tab
render_browse_tab(
    tab=tab_browse,
    name="Order Overview",
    view="v_browse_orders_page",
)

#Create Order Tab
render_create_order_tab(tab_create_order, engine, customers_df, employees_df, products_df)

#View or Update Order Details Tab
render_details_tab(tab_update_details, engine, orders_df, products_df)

#Delete Order Tab
render_delete_tab(
    tab=tab_delete,
    name="Delete Order",
    view="v_browse_orders_page",
    delete_id="Order ID",
    label_field_1="First Name",
    label_field_2="Last Name",
    label_field_3="Order Date",
    success_duration_seconds=ORDER_SUCCESS_MESSAGE_DURATION_SECONDS,
)
