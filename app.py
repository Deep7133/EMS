import streamlit as st
import mysql.connector
import pandas as pd

# ---------------- DB CONNECTION ----------------
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="employee_management"
    )

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="EMS", layout="wide")

# ---------------- SESSION STATE ----------------
if 'role' not in st.session_state:
    st.session_state['role'] = None
    st.session_state['id'] = None
    st.session_state['name'] = None

# ---------------- SIDEBAR ----------------
st.sidebar.title("🔐 Login Panel")
role_choice = st.sidebar.selectbox(
    "Select Role",
    ["Home", "Employee", "HR", "Admin"]
)

# ---------------- HOME ----------------
if role_choice == "Home":
    st.title("👨‍💼 Employee Management System")
    st.info("""
    • Employees can view attendance & salary  
    • HR marks attendance  
    • Admin manages system & analytics
    """)

# ======================================================
# ================= EMPLOYEE LOGIN =====================
# ======================================================
if role_choice == "Employee":

    if st.session_state['role'] != "employee":

        st.subheader("👨‍💼 Employee Login")
        email = st.text_input("Email")
        pwd = st.text_input("Password", type="password")

        if st.button("Login"):
            db = get_db()
            cur = db.cursor()
            cur.execute(
                "SELECT emp_id, emp_name FROM employees WHERE email=%s AND emp_pwd=%s",
                (email, pwd)
            )
            res = cur.fetchone()

            if res:
                st.session_state['role'] = "employee"
                st.session_state['id'] = res[0]
                st.session_state['name'] = res[1]
                st.rerun()
            else:
                st.error("Invalid credentials")

    else:
        st.sidebar.success(f"👋 {st.session_state['name']}")

        menu = st.sidebar.radio(
            "Employee Menu",
            ["My Attendance", "My Salary", "Apply for a Leave", "Leave Status", "Logout"]
        )

        db = get_db()
        cur = db.cursor()

        if menu == "My Attendance":
            st.subheader("📊 My Attendance")
            cur.execute(
                "SELECT date, status FROM attendance WHERE emp_id=%s ORDER BY date DESC",
                (st.session_state['id'],)
            )
            data = cur.fetchall()
            st.dataframe(pd.DataFrame(data, columns=["Date", "Status"]))

        elif menu == "My Salary":
            st.subheader("💰 My Salary")
            cur.execute(
                "SELECT month, total_salary FROM salary WHERE emp_id=%s",
                (st.session_state['id'],)
            )
            data = cur.fetchall()
            st.dataframe(pd.DataFrame(data, columns=["Month", "Salary"]))
        
        elif menu == "Apply for a Leave":
            st.subheader("📝 Apply for a Leave")

            leave_date = st.date_input("Leave Date")
            reason = st.text_area("Reason for Leave")

            if st.button("Submit Leave Request"):

                # 🔍 Check if leave already exists
                cur.execute(
                    """
                    SELECT status FROM leave_requests
                    WHERE emp_id=%s AND leave_date=%s
                    """,
                    (st.session_state['id'], leave_date)
                )
                existing = cur.fetchone()

                if existing:
                    st.warning(f"⚠️ Leave already requested for this date (Status: {existing[0]})")
                else:
                    cur.execute(
                        """
                        INSERT INTO leave_requests (emp_id, leave_date, reason, status)
                        VALUES (%s, %s, %s, 'Pending')
                        """,
                        (st.session_state['id'], leave_date, reason)
                    )
                    db.commit()
                    st.success("✅ Leave request submitted successfully")

        elif menu == "Leave Status":
            st.subheader("📋 My Leave Requests")
            cur.execute(
                "SELECT leave_date, reason, status FROM leave_requests WHERE emp_id=%s ORDER BY leave_date DESC",
                (st.session_state['id'],)
            )
            data = cur.fetchall()
            st.dataframe(pd.DataFrame(data, columns=["Leave Date", "Reason", "Status"]))

        elif menu == "Logout":
            st.session_state.clear()
            st.rerun()

# ======================================================
# ================= HR LOGIN ===========================
# ======================================================
if role_choice == "HR":

    if st.session_state['role'] != "hr":

        st.subheader("🧑‍💼 HR Login")
        email = st.text_input("Email")
        pwd = st.text_input("Password", type="password")

        if st.button("Login"):
            db = get_db()
            cur = db.cursor()
            cur.execute(
                "SELECT hr_id, hr_name FROM hr WHERE email=%s AND hr_pwd=%s",
                (email, pwd)
            )
            res = cur.fetchone()

            if res:
                st.session_state['role'] = "hr"
                st.session_state['id'] = res[0]
                st.session_state['name'] = res[1]
                st.rerun()
            else:
                st.error("Invalid credentials")

    else:
        st.sidebar.success(f"👋 {st.session_state['name']}")

        menu = st.sidebar.radio(
            "HR Menu",
            ["Mark Attendance", "View Attendance","Update Attendance", "Logout"]
        )

        db = get_db()
        cur = db.cursor()

        if menu == "Mark Attendance":
            st.subheader("⏱️ Mark Attendance")

            cur.execute("SELECT emp_id, emp_name FROM employees")
            emps = cur.fetchall()

            emp = st.selectbox(
                "Select Employee",
                emps,
                format_func=lambda x: f"{x[0]} - {x[1]}"
            )

            status = st.selectbox("Status", ["Present", "Absent", "Leave"])

            if st.button("Submit"):
                try:
                    cur.execute(
                        "INSERT INTO attendance (emp_id, date, status) VALUES (%s, CURDATE(), %s)",
                        (emp[0], status)
                    )
                    db.commit()
                    st.success("Attendance marked")
                except mysql.connector.IntegrityError:
                    st.warning("Attendance already marked for today")

        elif menu == "View Attendance":
            st.subheader("📋 Attendance Records")
            cur.execute("""
                SELECT e.emp_name, a.date, a.status
                FROM attendance a
                JOIN employees e ON a.emp_id = e.emp_id
                ORDER BY a.date DESC
            """)
            st.dataframe(pd.DataFrame(cur.fetchall(), columns=["Name", "Date", "Status"]))
        
        elif menu == "Update Attendance":
            st.subheader("✏️ Update Attendance")
            cur.execute("""
                SELECT a.emp_id, e.emp_name, a.date, a.status
                FROM attendance a
                JOIN employees e ON a.emp_id = e.emp_id
                ORDER BY a.date DESC
            """)
            records = cur.fetchall()
            record = st.selectbox(
                "Select Record",
                records,
                format_func=lambda x: f"{x[0]} - {x[1]} - {x[2]} - {x[3]}"
            )
            new_status = st.selectbox("New Status", ["Present", "Absent", "On leave"])
            if st.button("Update"):
                cur.execute(
                    "UPDATE attendance SET status=%s WHERE emp_id=%s",
                    (new_status, record[0])
                )
                db.commit()
                st.success("Attendance updated")

        elif menu == "Logout":
            st.session_state.clear()
            st.rerun()

# ======================================================
# ================= ADMIN LOGIN ========================
# ======================================================
if role_choice == "Admin":
    if st.session_state['role'] != "admin":
        st.subheader("👑 Admin Login")
        email = st.text_input("Admin Email")
        pwd = st.text_input("Password", type="password")

        if st.button("Login"):
            db = get_db()
            cur = db.cursor()
            cur.execute(
                "SELECT admin_id FROM admins WHERE admin_id=%s AND admin_pwd=%s",
                (email, pwd)
            )
            if cur.fetchone():
                st.session_state.update({"role": "admin", "name": email})
                st.rerun()
            else:
                st.error("Invalid admin")

    else:
        st.sidebar.success("👑 Admin")
        menu = st.sidebar.radio(
            "Admin Menu",
            ["Analytics","Add Employee", "Update Employee", "Delete Employee","approve leave", "Logout"]
        )

        db = get_db()
        cur = db.cursor()

        # -------- ADD EMPLOYEE --------
        if menu == "Add Employee":
            st.subheader("➕ Add Employee")
            with st.form("add_emp"):
                eid = st.text_input("Emp ID")
                name = st.text_input("Name")
                email = st.text_input("Email")
                pwd = st.text_input("Password")
                des = st.text_input("Designation")
                dep = st.text_input("Department")
                sal = st.text_input("Salary")
                if st.form_submit_button("Add"):
                    cur.execute(
                        "INSERT INTO employees VALUES (%s,%s,%s,%s,%s,%s,%s)",
                        (eid, name, email, pwd, des, dep, sal)
                    )
                    db.commit()
                    st.success("Employee Added")

        # -------- UPDATE EMPLOYEE --------
        elif menu == "Update Employee":
            st.subheader("✏️ Update Employee")
            emp_id = st.text_input("Employee ID")

            with st.form("update_emp"):
                name = st.text_input("New Name")
                email = st.text_input("New Email")
                pwd = st.text_input("New Password")
                des = st.text_input("New Designation")
                dep = st.text_input("New Department")
                sal = st.number_input("New Salary")
                if st.form_submit_button("Update"):
                    cur.execute("""
                        UPDATE employees SET emp_name=%s,email=%s,emp_pwd=%s,
                        designation=%s,department=%s,salary=%s WHERE emp_id=%s
                    """, (name, email, pwd, des, dep, sal, emp_id))
                    db.commit()
                    st.success("Employee Updated")

        # -------- DELETE EMPLOYEE --------
        elif menu == "Delete Employee":
            st.subheader("❌ Delete Employee")
            emp_id = st.text_input("Employee ID to delete")
            if st.button("Delete"):
                cur.execute("DELETE FROM employees WHERE emp_id=%s", (emp_id,))
                db.commit()
                st.success("Employee Deleted")

        # -------- APPROVE LEAVE REQUESTS --------
        elif menu == "approve leave":
            st.subheader("📝 Approve Leave Requests")
            db = mysql.connector.connect(host="localhost",username="root",password="root"
                                         ,database="employee_management")
            cur = db.cursor()
            cur.execute("""
                SELECT l.leave_id, e.emp_id, e.emp_name, l.leave_date, l.reason, l.status
                FROM leave_requests l
                JOIN employees e ON l.emp_id = e.emp_id
                WHERE l.status = 'Pending'
                ORDER BY l.leave_date
            """)

            leaves = cur.fetchall()

            if not leaves:
                st.success("No pending leave requests 🎉")
            else:
                df = pd.DataFrame(
                    leaves,
                    columns=["Leave ID", "Emp ID", "Employee Name", "Date", "Reason", "Status"]
                )
                st.dataframe(df, use_container_width=True)

                st.divider()

        # Select leave request
                leave_id = st.selectbox(
                    "Select Leave ID to take action",
                    df["Leave ID"].tolist()
                )

                action = st.radio("Action", ["Approved", "Rejected"])

                if st.button("Submit Decision"):

                    cur.execute(
                        "UPDATE leave_requests SET status=%s WHERE leave_id=%s",
                        (action, leave_id)
                    )

                    if action == "Approved":

                        # First update leave request
                        cur.execute(
                            "UPDATE leave_requests SET status='Approved' WHERE leave_id=%s",
                            (leave_id,)
                        )

                        # Then update / insert attendance
                        cur.execute("""
                            INSERT INTO attendance (emp_id, date, status)
                            SELECT emp_id, leave_date, 'On Leave'
                            FROM leave_requests
                            WHERE leave_id = %s
                            ON DUPLICATE KEY UPDATE status = 'On Leave'
                        """, (leave_id,))

                    db.commit()
                    st.success(f"Leave {action.lower()} successfully")
                    st.rerun()


        # -------- ANALYTICS --------
        elif menu == "Analytics":

            st.title("📊 Admin Dashboard")

            db = get_db()
            cur = db.cursor()

            # ==============================
            # KPIs SECTION
            # ==============================
            st.subheader("📌 Attendance KPIs")

            # Total Employees
            cur.execute("SELECT COUNT(*) FROM employees")
            total_employees = cur.fetchone()[0]

            # Total Present
            cur.execute("""
                SELECT COUNT(DISTINCT emp_id) 
                FROM attendance 
                WHERE date = CURDATE() AND status = 'Present'
            """)
            total_present = cur.fetchone()[0]

            # Total Absent
            cur.execute("""
                SELECT COUNT(DISTINCT emp_id) 
                FROM attendance 
                WHERE date = CURDATE() AND status = 'Absent'
            """)
            total_absent = cur.fetchone()[0]

            # Total On Leave
            cur.execute("""
                SELECT COUNT(DISTINCT emp_id) 
                FROM attendance 
                WHERE date = CURDATE() AND status = 'On leave'
            """)
            total_leave = cur.fetchone()[0]

            col1, col2, col3, col4 = st.columns(4)

            col1.metric("👥 Total Employees", total_employees)
            col2.metric("✅ Present Today", total_present)
            col3.metric("❌ Absent Today", total_absent)
            col4.metric("🏖️ On Leave ", total_leave)

            st.divider()

            # ==============================
            # EMPLOYEE MASTER TABLE
            # ==============================
            st.subheader("📋 Employee Details")

            cur.execute("""
                SELECT emp_name, designation, department, salary
                FROM employees
                ORDER BY emp_name
            """)

            emp_data = cur.fetchall()

            if emp_data:
                df = pd.DataFrame(
                    emp_data,
                    columns=["Employee Name", "Designation", "Department", "Salary"]
                )
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No employee data available")

        #logout option for admin
        elif menu == "Logout":
            st.session_state.clear()
            st.rerun()