import re
import uuid
from decimal import Decimal

from sqlalchemy import text


def sql_scalar(engine, query: str, params: dict | None = None):
    with engine.begin() as conn:
        return conn.execute(text(query), params or {}).scalar_one()


def sql_row(engine, query: str, params: dict | None = None):
    with engine.begin() as conn:
        return conn.execute(text(query), params or {}).mappings().first()


def sql_exec(engine, query: str, params: dict | None = None) -> None:
    with engine.begin() as conn:
        conn.execute(text(query), params or {})


def call_create(engine, create_id: str, p1=None, p2=None, p3=None, p4=None):
    with engine.begin() as conn:
        result = conn.execute(
            text("CALL sp_generic_create(:create_id, :p1, :p2, :p3, :p4);"),
            {
                "create_id": create_id,
                "p1": None if p1 is None else str(p1),
                "p2": None if p2 is None else str(p2),
                "p3": None if p3 is None else str(p3),
                "p4": None if p4 is None else str(p4),
            },
        )
        rows = result.fetchall() if result.returns_rows else []
        result.close()
        return rows


def call_update(engine, update_id: str, target_id, p1=None, p2=None, p3=None, p4=None):
    sql_exec(
        engine,
        "CALL sp_generic_update(:update_id, :target_id, :p1, :p2, :p3, :p4);",
        {
            "update_id": update_id,
            "target_id": str(target_id),
            "p1": None if p1 is None else str(p1),
            "p2": None if p2 is None else str(p2),
            "p3": None if p3 is None else str(p3),
            "p4": None if p4 is None else str(p4),
        },
    )


def call_delete(engine, delete_id: str, target_id):
    sql_exec(
        engine,
        "CALL sp_generic_delete(:delete_id, :target_id);",
        {"delete_id": delete_id, "target_id": str(target_id)},
    )


def token() -> str:
    return uuid.uuid4().hex[:8]


def go_to_page(page, page_name: str) -> None:
    page.get_by_role("link", name=page_name).click()
    page.wait_for_timeout(1000)


def open_tab(page, tab_name: str) -> None:
    page.get_by_role("tab", name=tab_name).click()
    page.wait_for_timeout(700)


def panel(page):
    return page.locator("[role='tabpanel']:visible").first


def choose_option(page, container, label: str, option_name: str) -> None:
    # Streamlit selectboxes expose aria-labels like:
    # "Selected <current option>. <field label>"
    label_pattern = re.compile(rf"{re.escape(label)}\s*$")
    option_locator = page.get_by_role("option", name=option_name).first
    last_error = None
    for _ in range(4):
        container.get_by_label(label_pattern).first.click()
        try:
            option_locator.click(timeout=3000)
            page.wait_for_timeout(400)
            return
        except Exception as exc:  # noqa: BLE001 - Playwright raises multiple exception types here.
            last_error = exc
            page.keyboard.press("Escape")
            page.wait_for_timeout(150)
    raise AssertionError(f"Failed to select option '{option_name}' for label '{label}'.") from last_error


def choose_option_regex(page, container, label: str, option_regex: str) -> None:
    label_pattern = re.compile(rf"{re.escape(label)}\s*$")
    option_locator = page.get_by_role("option", name=re.compile(option_regex)).first
    last_error = None
    for _ in range(4):
        container.get_by_label(label_pattern).first.click()
        try:
            option_locator.click(timeout=3000)
            page.wait_for_timeout(400)
            return
        except Exception as exc:  # noqa: BLE001 - Playwright raises multiple exception types here.
            last_error = exc
            page.keyboard.press("Escape")
            page.wait_for_timeout(150)
    raise AssertionError(f"Failed to select regex option '{option_regex}' for label '{label}'.") from last_error


def set_create_order_quantity(page, container, product_name: str, quantity: int) -> None:
    """Edit the create-order data editor by product row and set Quantity."""
    product_cells = container.locator("[data-testid^='glide-cell-1-']")
    row_count = product_cells.count()
    target_row = None
    for row_idx in range(row_count):
        if product_cells.nth(row_idx).inner_text().strip() == product_name:
            target_row = row_idx
            break

    assert target_row is not None, f"Product row '{product_name}' not found in create-order grid."

    grid_box = container.locator("[data-testid='stDataFrameResizable']").first.bounding_box()
    assert grid_box is not None, "Create-order data editor was not rendered."

    # Glide Data Editor renders cells on canvas; edit by cell coordinates.
    row_height = 35
    qty_cell = container.locator(f"[data-testid='glide-cell-3-{target_row}']")
    expected_text = str(int(quantity))

    for _ in range(2):
        for x_offset in (55, 65, 75, 85):
            target_x = grid_box["x"] + grid_box["width"] - x_offset
            for y_base in (64, 60, 56, 54, 58, 68):
                target_y = grid_box["y"] + y_base + (target_row * row_height)
                page.mouse.click(target_x, target_y)
                page.wait_for_timeout(80)
                page.mouse.dblclick(target_x, target_y)
                page.wait_for_timeout(80)
                page.keyboard.press("Control+A")
                page.keyboard.type(expected_text)
                page.keyboard.press("Enter")
                page.wait_for_timeout(200)
                if qty_cell.inner_text().strip() == expected_text:
                    return

    raise AssertionError(f"Unable to set quantity for product '{product_name}' to {expected_text}.")


def test_customers_page_crud_e2e(page, db_engine):
    t = token()
    first_name = f"E2ECust{t[:4]}"
    last_name = f"L{t[4:]}"
    full_label = f"{first_name} {last_name}"
    email = f"e2e_customer_{t}@example.com"
    updated_email = f"e2e_customer_updated_{t}@example.com"
    phone = f"555-10{t[:4]}"
    updated_phone = f"555-11{t[:4]}"
    customer_id = None

    try:
        go_to_page(page, "Customers")
        open_tab(page, "Create Customer")
        p = panel(page)
        p.get_by_label("First Name").fill(first_name)
        p.get_by_label("Last Name").fill(last_name)
        p.get_by_label("Email").fill(email)
        p.get_by_label("Phone Number").fill(phone)
        p.get_by_role("button", name="Create Customer").click()
        page.wait_for_timeout(1200)

        created = sql_row(
            db_engine,
            "SELECT customerID, firstName, lastName, email, phoneNumber FROM Customers WHERE email = :email;",
            {"email": email},
        )
        assert created is not None
        customer_id = int(created["customerID"])
        assert created["firstName"] == first_name
        assert created["lastName"] == last_name

        open_tab(page, "Update Customer")
        p = panel(page)
        choose_option(page, p, "Select Record", full_label)
        p.get_by_label("Email").fill(updated_email)
        p.get_by_label("Phone Number").fill(updated_phone)
        p.get_by_role("button", name="Update Customer").click()
        page.wait_for_timeout(1200)

        updated = sql_row(
            db_engine,
            "SELECT email, phoneNumber FROM Customers WHERE customerID = :customer_id;",
            {"customer_id": customer_id},
        )
        assert updated["email"] == updated_email
        assert updated["phoneNumber"] == updated_phone

        open_tab(page, "Delete Customer")
        p = panel(page)
        choose_option(page, p, "Select Record", full_label)
        p.get_by_role("button", name="Delete").click()
        page.wait_for_timeout(1200)

        remaining = int(
            sql_scalar(
                db_engine,
                "SELECT COUNT(*) FROM Customers WHERE customerID = :customer_id;",
                {"customer_id": customer_id},
            )
        )
        assert remaining == 0
        customer_id = None
    finally:
        if customer_id is not None:
            call_delete(db_engine, "Customer ID", customer_id)


def test_animals_page_crud_e2e(page, db_engine):
    t = token()
    name = f"E2EAnimal{t}"
    animal_id = None

    try:
        go_to_page(page, "Animals")
        open_tab(page, "Create Animal")
        p = panel(page)
        p.get_by_label("Name").fill(name)
        p.get_by_label("Species").fill("Gecko")
        p.get_by_label("Age").fill("2")
        p.get_by_label("Price").fill("123.45")
        p.get_by_role("button", name="Create Animal").click()
        page.wait_for_timeout(1200)

        created = sql_row(
            db_engine,
            "SELECT animalID, age, price, isAvailable FROM Animals WHERE name = :name;",
            {"name": name},
        )
        assert created is not None
        animal_id = int(created["animalID"])
        assert int(created["age"]) == 2
        assert created["price"] == Decimal("123.45")

        open_tab(page, "Update Animal")
        p = panel(page)
        choose_option_regex(page, p, "Select Record", rf"Animal ID:\s*{animal_id}\s+Name:\s*{re.escape(name)}\b")
        p.get_by_label("Age").fill("5")
        p.get_by_label("Price").fill("222.22")
        choose_option(page, p, "Available", "No")
        p.get_by_role("button", name="Update Animal").click()
        page.wait_for_timeout(1200)

        updated = sql_row(
            db_engine,
            "SELECT age, price, isAvailable FROM Animals WHERE animalID = :animal_id;",
            {"animal_id": animal_id},
        )
        assert int(updated["age"]) == 5
        assert updated["price"] == Decimal("222.22")
        assert int(updated["isAvailable"]) == 0

        open_tab(page, "Delete Animal")
        p = panel(page)
        choose_option_regex(page, p, "Select Record", rf"Animal ID:\s*{animal_id}\s+Name:\s*{re.escape(name)}\b")
        p.get_by_role("button", name="Delete").click()
        page.wait_for_timeout(1200)

        remaining = int(
            sql_scalar(
                db_engine,
                "SELECT COUNT(*) FROM Animals WHERE animalID = :animal_id;",
                {"animal_id": animal_id},
            )
        )
        assert remaining == 0
        animal_id = None
    finally:
        if animal_id is not None:
            call_delete(db_engine, "Animal ID", animal_id)


def test_employees_page_crud_e2e(page, db_engine):
    t = token()
    first_name = f"E2EEmp{t[:4]}"
    last_name = f"L{t[4:]}"
    full_label = f"{first_name} {last_name}"
    employee_id = None

    try:
        go_to_page(page, "Employees")
        open_tab(page, "Create Employee")
        p = panel(page)
        p.get_by_label("First Name").fill(first_name)
        p.get_by_label("Last Name").fill(last_name)
        p.get_by_label("Job Title").fill("Sales")
        p.get_by_role("button", name="Create Employee").click()
        page.wait_for_timeout(1200)

        created = sql_row(
            db_engine,
            "SELECT employeeID FROM Employees WHERE firstName = :first_name AND lastName = :last_name;",
            {"first_name": first_name, "last_name": last_name},
        )
        assert created is not None
        employee_id = int(created["employeeID"])

        open_tab(page, "Update Employee")
        p = panel(page)
        choose_option(page, p, "Select Record", full_label)
        p.get_by_label("First Name").fill(f"{first_name}U")
        p.get_by_label("Last Name").fill("Updated")
        p.get_by_label("Job Title").fill("Lead Sales")
        p.get_by_role("button", name="Update Employee").click()
        page.wait_for_timeout(1200)

        updated = sql_row(
            db_engine,
            "SELECT firstName, lastName, jobTitle FROM Employees WHERE employeeID = :employee_id;",
            {"employee_id": employee_id},
        )
        assert updated["firstName"] == f"{first_name}U"
        assert updated["lastName"] == "Updated"
        assert updated["jobTitle"] == "Lead Sales"

        open_tab(page, "Delete Employee")
        p = panel(page)
        choose_option_regex(page, p, "Select Record", rf"{re.escape(first_name)}")
        p.get_by_role("button", name="Delete").click()
        page.wait_for_timeout(1200)

        remaining = int(
            sql_scalar(
                db_engine,
                "SELECT COUNT(*) FROM Employees WHERE employeeID = :employee_id;",
                {"employee_id": employee_id},
            )
        )
        assert remaining == 0
        employee_id = None
    finally:
        if employee_id is not None:
            call_delete(db_engine, "Employee ID", employee_id)


def test_product_types_and_products_pages_crud_e2e(page, db_engine):
    t = token().upper()
    type_code = f"U{t[:7]}"
    type_name = f"E2EType{t}"
    product_name = f"E2EProduct{t}"
    product_id = None
    type_exists = False

    try:
        go_to_page(page, "Product Types")
        open_tab(page, "Create Product Type")
        p = panel(page)
        p.get_by_label("Product Type Code").fill(type_code)
        p.get_by_label("Product Type Name").fill(type_name)
        p.get_by_role("button", name="Create Product Type").click()
        page.wait_for_timeout(1200)

        created_type = sql_row(
            db_engine,
            "SELECT productTypeCode FROM ProductTypes WHERE productTypeCode = :code;",
            {"code": type_code},
        )
        assert created_type is not None
        type_exists = True

        open_tab(page, "Update Product Type")
        p = panel(page)
        choose_option(page, p, "Select Record", f"{type_code} {type_name}")
        p.get_by_label("Product Type Name").fill(f"{type_name}U")
        p.get_by_role("button", name="Update Product Type").click()
        page.wait_for_timeout(1200)
        updated_name = sql_scalar(
            db_engine,
            "SELECT productTypeName FROM ProductTypes WHERE productTypeCode = :code;",
            {"code": type_code},
        )
        assert updated_name == f"{type_name}U"

        go_to_page(page, "Products")
        open_tab(page, "Create Product")
        p = panel(page)
        p.get_by_label("Product Name").fill(product_name)
        choose_option(page, p, "Product Type", type_code)
        p.get_by_label("Price").fill("10.50")
        p.get_by_label("Stock").fill("7")
        p.get_by_role("button", name="Create Product").click()
        page.wait_for_timeout(1200)

        created_product = sql_row(
            db_engine,
            "SELECT productID, productTypeCode, price, stock FROM Products WHERE productName = :name;",
            {"name": product_name},
        )
        assert created_product is not None
        product_id = int(created_product["productID"])
        assert created_product["productTypeCode"] == type_code

        open_tab(page, "Update Product")
        p = panel(page)
        choose_option(page, p, "Select Record", product_name)
        p.get_by_label("Product Name").fill(f"{product_name}U")
        choose_option(page, p, "Product Type", "LGT")
        p.get_by_label("Price").fill("20.25")
        p.get_by_label("Stock").fill("3")
        p.get_by_role("button", name="Update Product").click()
        page.wait_for_timeout(1200)

        updated_product = sql_row(
            db_engine,
            "SELECT productName, productTypeCode, price, stock FROM Products WHERE productID = :product_id;",
            {"product_id": product_id},
        )
        assert updated_product["productName"] == f"{product_name}U"
        assert updated_product["productTypeCode"] == "LGT"
        assert updated_product["price"] == Decimal("20.25")
        assert int(updated_product["stock"]) == 3

        open_tab(page, "Delete Product")
        p = panel(page)
        choose_option_regex(page, p, "Select Record", rf"{re.escape(product_name)}")
        p.get_by_role("button", name="Delete").click()
        page.wait_for_timeout(1200)

        remaining_product = int(
            sql_scalar(
                db_engine,
                "SELECT COUNT(*) FROM Products WHERE productID = :product_id;",
                {"product_id": product_id},
            )
        )
        assert remaining_product == 0
        product_id = None

        go_to_page(page, "Product Types")
        open_tab(page, "Delete Product Type")
        p = panel(page)
        choose_option_regex(page, p, "Select Record", rf"{re.escape(type_code)}")
        p.get_by_role("button", name="Delete").click()
        page.wait_for_timeout(1200)

        remaining_type = int(
            sql_scalar(
                db_engine,
                "SELECT COUNT(*) FROM ProductTypes WHERE productTypeCode = :code;",
                {"code": type_code},
            )
        )
        assert remaining_type == 0
        type_exists = False
    finally:
        if product_id is not None:
            call_delete(db_engine, "Product ID", product_id)
        if type_exists:
            call_delete(db_engine, "Product Type Code", type_code)


def test_employee_assignments_page_crud_e2e(page, db_engine):
    t = token()
    employee_1_id = None
    employee_2_id = None
    animal_id = None
    assignment_id = None

    try:
        call_create(db_engine, "Employee", f"E2EA{t}", "One", "Specialist", None)
        call_create(db_engine, "Employee", f"E2EB{t}", "Two", "Specialist", None)
        call_create(db_engine, "Animal", f"E2EAssignAnimal{t}", "Gecko", 1, "99.99")

        employee_1_id = int(
            sql_scalar(
                db_engine,
                "SELECT employeeID FROM Employees WHERE firstName = :first_name AND lastName = 'One';",
                {"first_name": f"E2EA{t}"},
            )
        )
        employee_2_id = int(
            sql_scalar(
                db_engine,
                "SELECT employeeID FROM Employees WHERE firstName = :first_name AND lastName = 'Two';",
                {"first_name": f"E2EB{t}"},
            )
        )
        animal_id = int(
            sql_scalar(
                db_engine,
                "SELECT animalID FROM Animals WHERE name = :name;",
                {"name": f"E2EAssignAnimal{t}"},
            )
        )

        go_to_page(page, "Employee Assignments")
        open_tab(page, "Create Assignment")
        p = panel(page)
        choose_option_regex(page, p, "Animal", rf"^Animal ID:\s*{animal_id}\s+Animal Name:")
        choose_option_regex(page, p, "Employee", rf"^{employee_1_id} - ")
        p.get_by_role("button", name="Create Assignment").click()
        page.wait_for_timeout(1200)

        assignment_id = int(
            sql_scalar(
                db_engine,
                "SELECT animalDetailsID FROM EmployeeAnimals "
                "WHERE animalID = :animal_id AND employeeID = :employee_id "
                "ORDER BY animalDetailsID DESC LIMIT 1;",
                {"animal_id": animal_id, "employee_id": employee_1_id},
            )
        )

        open_tab(page, "Update Assignment")
        p = panel(page)
        choose_option_regex(page, p, "Select Record", rf"^{assignment_id} ")
        choose_option_regex(page, p, "Animal", rf"^Animal ID:\s*{animal_id}\s+Animal Name:")
        choose_option_regex(page, p, "Employee", rf"^{employee_2_id} - ")
        p.get_by_role("button", name="Update Assignment").click()
        page.wait_for_timeout(1200)

        updated = sql_row(
            db_engine,
            "SELECT animalID, employeeID FROM EmployeeAnimals WHERE animalDetailsID = :assignment_id;",
            {"assignment_id": assignment_id},
        )
        assert int(updated["animalID"]) == animal_id
        assert int(updated["employeeID"]) == employee_2_id

        open_tab(page, "Delete Assignment")
        p = panel(page)
        choose_option_regex(page, p, "Select Record", rf"^{assignment_id} ")
        p.get_by_role("button", name="Delete").click()
        page.wait_for_timeout(1200)

        remaining = int(
            sql_scalar(
                db_engine,
                "SELECT COUNT(*) FROM EmployeeAnimals WHERE animalDetailsID = :assignment_id;",
                {"assignment_id": assignment_id},
            )
        )
        assert remaining == 0
        assignment_id = None
    finally:
        if assignment_id is not None:
            call_delete(db_engine, "Assignment ID", assignment_id)
        if animal_id is not None and int(
            sql_scalar(
                db_engine,
                "SELECT COUNT(*) FROM Animals WHERE animalID = :animal_id;",
                {"animal_id": animal_id},
            )
        ) > 0:
            call_delete(db_engine, "Animal ID", animal_id)
        if employee_1_id is not None and int(
            sql_scalar(
                db_engine,
                "SELECT COUNT(*) FROM Employees WHERE employeeID = :employee_id;",
                {"employee_id": employee_1_id},
            )
        ) > 0:
            call_delete(db_engine, "Employee ID", employee_1_id)
        if employee_2_id is not None and int(
            sql_scalar(
                db_engine,
                "SELECT COUNT(*) FROM Employees WHERE employeeID = :employee_id;",
                {"employee_id": employee_2_id},
            )
        ) > 0:
            call_delete(db_engine, "Employee ID", employee_2_id)


def test_orders_page_update_delete_and_create_validation_e2e(page, db_engine):
    t = token()
    customer_email = f"e2e_order_customer_{t}@example.com"
    product_name = None
    customer_id = None
    employee_id = None
    product_id = None
    order_id = None

    try:
        call_create(db_engine, "Customer", f"E2EOrder{t}", "Customer", customer_email, f"555-40{t[:4]}")
        call_create(db_engine, "Employee", f"E2EOrder{t}", "Employee", "Sales", None)

        customer_id = int(
            sql_scalar(
                db_engine,
                "SELECT customerID FROM Customers WHERE email = :email;",
                {"email": customer_email},
            )
        )
        employee_id = int(
            sql_scalar(
                db_engine,
                "SELECT employeeID FROM Employees WHERE firstName = :first_name AND lastName = 'Employee';",
                {"first_name": f"E2EOrder{t}"},
            )
        )
        product_row = sql_row(
            db_engine,
            "SELECT productID, productName FROM Products ORDER BY productID LIMIT 1;",
        )
        assert product_row is not None
        product_id = int(product_row["productID"])
        product_name = str(product_row["productName"])
        go_to_page(page, "Orders")

        open_tab(page, "Create Order")
        p = panel(page)
        choose_option_regex(page, p, "Customer", rf"E2EOrder{t}\s+Customer")
        choose_option_regex(page, p, "Assigned Employee", rf"E2EOrder{t}\s+Employee")
        p.get_by_role("button", name="Create Order").click()
        page.wait_for_timeout(900)
        assert page.get_by_text("must contain atleast one item").count() >= 1

        set_create_order_quantity(page, p, product_name, 2)
        p.get_by_role("button", name="Create Order").click()
        page.wait_for_timeout(1500)

        created_order = sql_row(
            db_engine,
            "SELECT orderID, orderTotal FROM Orders "
            "WHERE customerID = :customer_id AND employeeID = :employee_id "
            "ORDER BY orderID DESC LIMIT 1;",
            {"customer_id": customer_id, "employee_id": employee_id},
        )
        assert created_order is not None
        order_id = int(created_order["orderID"])

        created_detail = sql_row(
            db_engine,
            "SELECT quantity, unitPrice FROM OrderDetails "
            "WHERE orderID = :order_id AND productID = :product_id;",
            {"order_id": order_id, "product_id": product_id},
        )
        assert created_detail is not None
        assert int(created_detail["quantity"]) == 2
        assert created_order["orderTotal"] == Decimal("2") * created_detail["unitPrice"]

        open_tab(page, "View or Update Order Details")
        p = panel(page)
        choose_option_regex(page, p, "Order", rf"Order ID: {order_id}\b")
        choose_option(page, p, "Select Item", product_name)
        p.get_by_label("Quantity").fill("5")
        p.get_by_role("button", name="Update or Add Item").click()
        page.wait_for_timeout(1200)

        updated = sql_row(
            db_engine,
            "SELECT quantity, unitPrice FROM OrderDetails "
            "WHERE orderID = :order_id AND productID = :product_id;",
            {"order_id": order_id, "product_id": product_id},
        )
        assert int(updated["quantity"]) == 5
        total = sql_scalar(
            db_engine,
            "SELECT orderTotal FROM Orders WHERE orderID = :order_id;",
            {"order_id": order_id},
        )
        assert total == Decimal("5") * updated["unitPrice"]

        open_tab(page, "Delete Order")
        p = panel(page)
        choose_option_regex(page, p, "Select Record", rf"E2EOrder{t}\s+Customer")
        p.get_by_role("button", name="Delete").click()
        page.wait_for_timeout(1200)

        remaining_order = int(
            sql_scalar(
                db_engine,
                "SELECT COUNT(*) FROM Orders WHERE orderID = :order_id;",
                {"order_id": order_id},
            )
        )
        remaining_details = int(
            sql_scalar(
                db_engine,
                "SELECT COUNT(*) FROM OrderDetails WHERE orderID = :order_id;",
                {"order_id": order_id},
            )
        )
        assert remaining_order == 0
        assert remaining_details == 0
        order_id = None
    finally:
        if order_id is not None:
            call_delete(db_engine, "Order ID", order_id)
        if customer_id is not None and int(
            sql_scalar(
                db_engine,
                "SELECT COUNT(*) FROM Customers WHERE customerID = :customer_id;",
                {"customer_id": customer_id},
            )
        ) > 0:
            call_delete(db_engine, "Customer ID", customer_id)
        if employee_id is not None and int(
            sql_scalar(
                db_engine,
                "SELECT COUNT(*) FROM Employees WHERE employeeID = :employee_id;",
                {"employee_id": employee_id},
            )
        ) > 0:
            call_delete(db_engine, "Employee ID", employee_id)


def test_zz_reset_button_restores_seed_data_e2e(page, db_engine):
    t = token()
    temp_email = f"e2e_reset_{t}@example.com"
    temp_phone = f"555-90{t[:4]}"

    call_create(db_engine, "Customer", "Reset", "Target", temp_email, temp_phone)
    assert int(
        sql_scalar(
            db_engine,
            "SELECT COUNT(*) FROM Customers WHERE email = :email;",
            {"email": temp_email},
        )
    ) == 1

    go_to_page(page, "Orders")
    page.get_by_role("button", name="Reset Database").click()
    page.wait_for_timeout(2000)

    assert int(
        sql_scalar(
            db_engine,
            "SELECT COUNT(*) FROM Customers WHERE email = :email;",
            {"email": temp_email},
        )
    ) == 0

    expected_seed_counts = {
        "Customers": 3,
        "Employees": 3,
        "Orders": 3,
        "ProductTypes": 3,
        "Products": 3,
        "Animals": 3,
        "OrderDetails": 6,
        "EmployeeAnimals": 3,
    }
    for table_name, expected_count in expected_seed_counts.items():
        actual_count = int(sql_scalar(db_engine, f"SELECT COUNT(*) FROM {table_name};"))
        assert actual_count == expected_count, (
            f"{table_name} count after reset expected {expected_count}, got {actual_count}"
        )


def test_friendly_error_product_type_delete_constraint_e2e(page):
    go_to_page(page, "Product Types")
    open_tab(page, "Delete Product Type")
    p = panel(page)
    choose_option_regex(page, p, "Select Record", r"^ENC\b")
    p.get_by_role("button", name="Delete").click()
    page.wait_for_timeout(1200)

    assert (
        page.get_by_text(
            "SQL ERROR: Cannot delete this item as a constraint prevents you from doing so."
        ).count()
        >= 1
    )


def test_friendly_error_customer_unique_violation_e2e(page, db_engine):
    seed_email = str(
        sql_scalar(
            db_engine,
            "SELECT email FROM Customers ORDER BY customerID LIMIT 1;",
        )
    )
    t = token()

    go_to_page(page, "Customers")
    open_tab(page, "Create Customer")
    p = panel(page)
    p.get_by_label("First Name").fill(f"Dup{t[:4]}")
    p.get_by_label("Last Name").fill("Email")
    p.get_by_label("Email").fill(seed_email)
    p.get_by_label("Phone Number").fill(f"555-77{t[:4]}")
    p.get_by_role("button", name="Create Customer").click()
    page.wait_for_timeout(1200)

    assert page.get_by_text("SQL ERROR: Duplicate value violates a unique constraint.").count() >= 1
