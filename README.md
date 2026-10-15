# Employee Management System (EMS)

A Python-based Employee Management System built with Streamlit, MySQL, and Pandas.

## Features
- Employee login, attendance and salary viewing
- Leave application and status tracking
- HR attendance marking, viewing and updating
- Admin employee management (add, update, delete)
- Leave request approval and rejection
- Attendance analytics dashboard

## Tech Stack
- Python
- Streamlit
- MySQL
- mysql-connector-python
- Pandas

## Installation
1. Install Python and MySQL.
2. Install dependencies:

   pip install -r requirements.txt

3. Create a MySQL database named employee_management and configure the required tables.
4. Configure the database connection in app.py.
5. Run the app:

   streamlit run app.py

Open the local URL shown in the terminal, usually http://localhost:8501.

## Database Tables
The application references employees, hr, admins, attendance, salary, and leave_requests.

Note: The database schema must be created separately. This project has not yet been deployed. Do not publish real database credentials or employee data.
