"""
main.py
Smart Student Record Management System (SSRMS)
- Login (users table)
- Dashboard with modules: Students, Departments, Courses, Results, Attendance
- Full CRUD with correct bind ordering (avoids ORA-01036)
- ERD feature removed per request
- Set DB_PASSWORD before running
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext  # noqa: F401
import cx_Oracle
import traceback  # noqa: F401

# ------------------ DB CONFIG ------------------
DB_HOST = "localhost"
DB_PORT = 1521
DB_SERVICE = "XE"
DB_USER = "HR"
DB_PASSWORD = "12345678"  # <-- set your Oracle password here

def make_connection():
    dsn = cx_Oracle.makedsn(DB_HOST, DB_PORT, service_name=DB_SERVICE)
    return cx_Oracle.connect(user=DB_USER, password=DB_PASSWORD, dsn=dsn)

try:
    CONN = make_connection()
except Exception as e:  # noqa: E722
    CONN = None
    print("Database connection failed:", e)

# ------------------ DB HELPERS ------------------
def fetch_all(query, params=None):
    cur = CONN.cursor()
    cur.execute(query, params or {})
    rows = cur.fetchall()
    cur.close()
    return rows

def execute(query, params=None):
    cur = CONN.cursor()
    cur.execute(query, params or {})
    CONN.commit()
    cur.close()

# ------------------ THEME ------------------
COLOR_BG = "#0b1220"
COLOR_CARD = "#071029"
COLOR_HEADER = "#0f1724"
COLOR_ACCENT = "#2563eb"
COLOR_SUCCESS = "#16a34a"
COLOR_WARN = "#f59e0b"
COLOR_DANGER = "#dc2626"
COLOR_TEXT = "#e6eef8"
FONT_TITLE = ("Segoe UI", 18, "bold")  # noqa: TYP001
FONT_SECTION = ("Segoe UI", 13, "bold")  # noqa: TYP001
FONT_TEXT = ("Segoe UI", 10)  # noqa: TYP001

# ------------------ TREE STYLE & SORT ------------------
def style_tree():
    style = ttk.Style()
    style.theme_use("default")
    style.configure("Treeview",
                    background="#071029",
                    foreground=COLOR_TEXT,
                    fieldbackground="#071029",
                    rowheight=26,
                    font=FONT_TEXT)
    style.configure("Treeview.Heading",
                    background="#0f1724",
                    foreground=COLOR_TEXT,
                    font=("Segoe UI", 10, "bold"))  # noqa: TYP001
    style.map("Treeview",
              background=[("selected", COLOR_ACCENT)],
              foreground=[("selected", "#ffffff")])

def make_sortable(tree: ttk.Treeview):
    def sortby(col, descending):
        data = [(tree.set(k, col), k) for k in tree.get_children('')]
        try:
            data.sort(key=lambda t: float(t[0]) if t[0] != "" else float("-inf"), reverse=descending)
        except Exception:  # noqa: E722
            data.sort(key=lambda t: str(t[0]).lower(), reverse=descending)
        for index, (_, k) in enumerate(data):
            tree.move(k, '', index)
        tree.heading(col, command=lambda: sortby(col, not descending))
    for c in tree["columns"]:  # noqa: F811
        tree.heading(c, command=lambda col=c: sortby(col, False))

# ------------------ GENERIC CRUD PAGE BUILDER ------------------
def build_crud_page(parent, title, columns, labels, pk_cols, queries):
    """
    columns: list of DB column names in display order (including PKs)
    pk_cols: list of PK column names (subset of columns)
    queries: dict with keys select_all, insert, update, delete, search
      - update must accept parameters in order:
        (all non-pk columns in order) followed by (pk columns in order)
    """
    frame = tk.Frame(parent, bg=COLOR_BG)
    frame.pack(fill="both", expand=True)

    header = tk.Label(frame, text=title, bg=COLOR_HEADER, fg=COLOR_TEXT, font=FONT_SECTION, anchor="w", padx=12)
    header.pack(fill="x", pady=(0, 8))

    card = tk.Frame(frame, bg=COLOR_CARD, padx=12, pady=12)
    card.pack(fill="both", expand=True, padx=12, pady=8)

    # Form (left)
    form = tk.Frame(card, bg=COLOR_CARD)
    form.pack(side="left", fill="y", padx=(0, 12))
    entries = {}
    for i, (lab, col) in enumerate(zip(labels, columns)):
        lbl = tk.Label(form, text=lab, bg=COLOR_CARD, fg=COLOR_TEXT, font=FONT_TEXT, anchor="w")
        lbl.grid(row=i, column=0, sticky="w", pady=6)
        ent = tk.Entry(form, width=30, bg="#0b1b2b", fg=COLOR_TEXT, insertbackground=COLOR_TEXT)
        ent.grid(row=i, column=1, pady=6, padx=(8, 0))
        entries[col] = ent

    btn_frame = tk.Frame(form, bg=COLOR_CARD)
    btn_frame.grid(row=len(columns), column=0, columnspan=2, pady=(12, 0))

    # Table (right)
    table_frame = tk.Frame(card, bg=COLOR_CARD)
    table_frame.pack(side="right", fill="both", expand=True)

    tree = ttk.Treeview(table_frame, columns=columns, show="headings")
    for c, lab in zip(columns, labels):  # noqa: F811
        tree.heading(c, text=lab)
        tree.column(c, width=140, anchor="w")
    tree.pack(fill="both", expand=True, padx=6, pady=6)

    style_tree()
    tree.tag_configure("odd", background="#071029")
    tree.tag_configure("even", background="#0e1a2b")
    make_sortable(tree)

    def insert_rows(rows):
        tree.delete(*tree.get_children())
        for i, r in enumerate(rows):
            tag = "even" if i % 2 == 0 else "odd"
            tree.insert("", "end", values=r, tags=(tag,))

    def load_all():
        try:
            rows = fetch_all(queries["select_all"])
            insert_rows(rows)
        except Exception as e:  # noqa: E722
            messagebox.showerror("Error", f"Failed to load data:\n{e}")

    def add_record():
        vals = tuple(entries[c].get().strip() for c in columns)
        try:
            execute(queries["insert"], vals)
            load_all()
            messagebox.showinfo("Success", "Record added.")
        except Exception as e:  # noqa: E722
            messagebox.showerror("Error", f"Insert failed:\n{e}")

    def update_record():
        # Build params as: (non-pk columns in order) + (pk columns in order)
        non_pk_cols = [c for c in columns if c not in pk_cols]
        params = tuple(entries[c].get().strip() for c in non_pk_cols) + tuple(entries[c].get().strip() for c in pk_cols)
        try:
            execute(queries["update"], params)
            load_all()
            messagebox.showinfo("Success", "Record updated.")
        except Exception as e:  # noqa: E722
            messagebox.showerror("Error", f"Update failed:\n{e}")

    def delete_record():
        where_vals = tuple(entries[c].get().strip() for c in pk_cols)
        try:
            execute(queries["delete"], where_vals)
            load_all()
            messagebox.showinfo("Success", "Record deleted.")
        except Exception as e:  # noqa: E722
            messagebox.showerror("Error", f"Delete failed:\n{e}")

    def search_record():
        key = entries[pk_cols[0]].get().strip()
        try:
            rows = fetch_all(queries["search"], (key,))
            insert_rows(rows)
        except Exception as e:  # noqa: E722
            messagebox.showerror("Error", f"Search failed:\n{e}")

    tk.Button(btn_frame, text="Add", bg=COLOR_SUCCESS, fg="white", width=10, command=add_record).grid(row=0, column=0, padx=6)
    tk.Button(btn_frame, text="Update", bg=COLOR_WARN, fg="white", width=10, command=update_record).grid(row=0, column=1, padx=6)
    tk.Button(btn_frame, text="Delete", bg=COLOR_DANGER, fg="white", width=10, command=delete_record).grid(row=0, column=2, padx=6)
    tk.Button(btn_frame, text="Search", bg=COLOR_ACCENT, fg="white", width=10, command=search_record).grid(row=0, column=3, padx=6)
    tk.Button(btn_frame, text="Refresh", bg="#334155", fg="white", width=10, command=load_all).grid(row=0, column=4, padx=6)

    def on_select(event):  # noqa: ARG001

        sel = tree.selection()
        if not sel:
            return
        vals = tree.item(sel[0])["values"]
        for col, val in zip(columns, vals):
            entries[col].delete(0, tk.END)
            entries[col].insert(0, "" if val is None else str(val))

    tree.bind("<<TreeviewSelect>>", on_select)
    load_all()
    return frame

# ------------------ MODULE PAGES ------------------
def page_students(parent):
    cols = ["roll_no", "first_name", "last_name", "gender", "date_of_birth", "email", "phone", "address", "department", "semester"]
    labels = ["Roll No", "First Name", "Last Name", "Gender", "DOB (YYYY-MM-DD)", "Email", "Phone", "Address", "Department", "Semester"]
    queries = {
        "select_all": """SELECT roll_no, first_name, last_name, gender,
                                TO_CHAR(date_of_birth,'YYYY-MM-DD'),
                                email, phone, address, department, semester
                         FROM students""",
        "insert": """INSERT INTO students (roll_no, first_name, last_name, gender, date_of_birth, email, phone, address, department, semester)
                     VALUES (:1, :2, :3, :4, TO_DATE(:5,'YYYY-MM-DD'), :6, :7, :8, :9, :10)""",
        # update expects non-pk columns first (first_name..semester) then pk roll_no as last bind
        "update": """UPDATE students SET first_name=:1, last_name=:2, gender=:3,
                                       date_of_birth=TO_DATE(:4,'YYYY-MM-DD'),
                                       email=:5, phone=:6, address=:7, department=:8, semester=:9
                     WHERE roll_no=:10""",
        "delete": "DELETE FROM students WHERE roll_no=:1",
        "search": """SELECT roll_no, first_name, last_name, gender,
                            TO_CHAR(date_of_birth,'YYYY-MM-DD'),
                            email, phone, address, department, semester
                     FROM students WHERE roll_no=:1"""
    }
    return build_crud_page(parent, "Students", cols, labels, ["roll_no"], queries)

def page_departments(parent):
    cols = ["dept_id", "dept_name", "hod_name", "hod_email"]
    labels = ["Dept ID", "Dept Name", "HOD Name", "HOD Email"]
    queries = {
        "select_all": "SELECT dept_id, dept_name, hod_name, hod_email FROM departments",
        "insert": "INSERT INTO departments (dept_id, dept_name, hod_name, hod_email) VALUES (:1, :2, :3, :4)",
        "update": "UPDATE departments SET dept_name=:1, hod_name=:2, hod_email=:3 WHERE dept_id=:4",
        "delete": "DELETE FROM departments WHERE dept_id=:1",
        "search": "SELECT dept_id, dept_name, hod_name, hod_email FROM departments WHERE dept_id=:1"
    }
    return build_crud_page(parent, "Departments", cols, labels, ["dept_id"], queries)

def page_courses(parent):
    cols = ["course_id", "course_name", "credits", "description"]
    labels = ["Course ID", "Course Name", "Credits", "Description"]
    queries = {
        "select_all": "SELECT course_id, course_name, credits, description FROM courses",
        "insert": "INSERT INTO courses (course_id, course_name, credits, description) VALUES (:1,:2,:3,:4)",
        "update": "UPDATE courses SET course_name=:1, credits=:2, description=:3 WHERE course_id=:4",
        "delete": "DELETE FROM courses WHERE course_id=:1",
        "search": "SELECT course_id, course_name, credits, description FROM courses WHERE course_id=:1"
    }
    return build_crud_page(parent, "Courses", cols, labels, ["course_id"], queries)

def page_results(parent):
    cols = ["roll_no", "course", "grade", "remarks"]
    labels = ["Roll No", "Course", "Grade", "Remarks"]
    queries = {
        "select_all": "SELECT roll_no, course, grade, remarks FROM results",
        "insert": "INSERT INTO results (roll_no, course, grade, remarks) VALUES (:1,:2,:3,:4)",
        # update expects non-pk cols (grade, remarks) then pk roll_no, course
        "update": "UPDATE results SET grade=:1, remarks=:2 WHERE roll_no=:3 AND course=:4",
        "delete": "DELETE FROM results WHERE roll_no=:1 AND course=:2",
        "search": "SELECT roll_no, course, grade, remarks FROM results WHERE roll_no=:1"
    }
    return build_crud_page(parent, "Results", cols, labels, ["roll_no", "course"], queries)

def page_attendance(parent):
    cols = ["roll_no", "course", "attendance_percent", "present_days", "total_days"]
    labels = ["Roll No", "Course", "Attendance %", "Present Days", "Total Days"]
    queries = {
        "select_all": "SELECT roll_no, course, attendance_percent, present_days, total_days FROM attendance",
        "insert": "INSERT INTO attendance (roll_no, course, attendance_percent, present_days, total_days) VALUES (:1,:2,:3,:4,:5)",
        # update expects non-pk cols (attendance_percent, present_days, total_days) then pk roll_no, course
        "update": "UPDATE attendance SET attendance_percent=:1, present_days=:2, total_days=:3 WHERE roll_no=:4 AND course=:5",
        "delete": "DELETE FROM attendance WHERE roll_no=:1 AND course=:2",
        "search": "SELECT roll_no, course, attendance_percent, present_days, total_days FROM attendance WHERE roll_no=:1"
    }
    return build_crud_page(parent, "Attendance", cols, labels, ["roll_no", "course"], queries)

# ------------------ DASHBOARD ------------------
def open_dashboard(user, role):
    app = tk.Tk()
    app.title("SSRMS • Dashboard")
    app.geometry("1200x760")
    app.configure(bg=COLOR_BG)

    header = tk.Frame(app, bg=COLOR_HEADER, height=64)
    header.pack(side="top", fill="x")
    tk.Label(header, text="Smart Student Record Management System", bg=COLOR_HEADER, fg=COLOR_TEXT, font=FONT_TITLE).pack(side="left", padx=16)
    tk.Label(header, text="Empowering Students, Inspiring Futures", bg=COLOR_HEADER, fg="#9fb4ff", font=FONT_TEXT).pack(side="left", padx=12)
    tk.Label(header, text=f"User: {user} • Role: {role}", bg=COLOR_HEADER, fg="#93c5fd", font=FONT_TEXT).pack(side="right", padx=16)

    sidebar = tk.Frame(app, bg="#071029", width=220)
    sidebar.pack(side="left", fill="y")

    btn_cfg = {"bg": COLOR_ACCENT, "fg": "white", "font": FONT_TEXT, "relief": "flat", "activebackground": "#1e3a8a"}

    content = tk.Frame(app, bg=COLOR_BG)
    content.pack(side="right", fill="both", expand=True)

    current_page = {"frame": None}
    def load_page(builder):
        if current_page["frame"]:
            current_page["frame"].destroy()  # noqa: E1101
        current_page["frame"] = tk.Frame(content, bg=COLOR_BG)
        current_page["frame"].pack(fill="both", expand=True)
        builder(current_page["frame"])

    tk.Button(sidebar, text="Students", width=20, command=lambda: load_page(page_students), **btn_cfg).pack(pady=8, padx=12)
    tk.Button(sidebar, text="Departments", width=20, command=lambda: load_page(page_departments), **btn_cfg).pack(pady=8, padx=12)
    tk.Button(sidebar, text="Courses", width=20, command=lambda: load_page(page_courses), **btn_cfg).pack(pady=8, padx=12)
    tk.Button(sidebar, text="Results", width=20, command=lambda: load_page(page_results), **btn_cfg).pack(pady=8, padx=12)
    tk.Button(sidebar, text="Attendance", width=20, command=lambda: load_page(page_attendance), **btn_cfg).pack(pady=8, padx=12)
    # ERD feature intentionally removed

    load_page(page_students)
    app.mainloop()

# ------------------ LOGIN WINDOW ------------------
def show_login():
    root = tk.Tk()
    root.title("SSRMS • Login")
    root.geometry("420x360")
    root.configure(bg=COLOR_BG)

    card = tk.Frame(root, bg=COLOR_CARD, padx=16, pady=16)
    card.pack(expand=True, padx=24, pady=24, fill="both")

    tk.Label(card, text="Login to SSRMS", bg=COLOR_CARD, fg=COLOR_TEXT, font=FONT_SECTION).pack(pady=(0,12))
    tk.Label(card, text="Username", bg=COLOR_CARD, fg=COLOR_TEXT).pack(anchor="w")
    user_entry = tk.Entry(card, bg="#0b1b2b", fg=COLOR_TEXT, insertbackground=COLOR_TEXT)
    user_entry.pack(fill="x", pady=6)
    user_entry.insert(0, "admin")

    tk.Label(card, text="Password", bg=COLOR_CARD, fg=COLOR_TEXT).pack(anchor="w", pady=(8,0))
    pass_entry = tk.Entry(card, show="*", bg="#0b1b2b", fg=COLOR_TEXT, insertbackground=COLOR_TEXT)
    pass_entry.pack(fill="x", pady=6)
    pass_entry.insert(0, "admin123")

    def do_login():
        username_val = user_entry.get().strip()
        password_val = pass_entry.get().strip()
        try:
            rows = fetch_all("SELECT role FROM users WHERE username=:u AND password=:p", {"u": username_val, "p": password_val})
            if rows:
                role = rows[0][0]
                root.destroy()
                open_dashboard(username_val, role)
            else:
                messagebox.showerror("Login Failed", "Invalid username or password.")
        except Exception as e:  # noqa: E722
            messagebox.showerror("Error", f"Login error:\n{e}")

    tk.Button(card, text="Login", bg=COLOR_ACCENT, fg="white", width=20, command=do_login).pack(pady=12)
    tk.Label(card, text="Empowering Students, Inspiring Futures", bg=COLOR_CARD, fg="#93c5fd", font=("Segoe UI",9,"italic")).pack(pady=(8,0))  # noqa: TYP001
    root.mainloop()

# ------------------ START ------------------
if __name__ == "__main__":
    if CONN is None:
        print("Unable to connect to the database. Update DB credentials and ensure Oracle is reachable.")
    else:
        show_login()
        CONN.close()
