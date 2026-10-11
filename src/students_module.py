import tkinter as tk
from tkinter import ttk, messagebox
import cx_Oracle

def open_students(conn):
    win = tk.Toplevel()
    win.title("Students Management")
    win.geometry("950x600")
    win.configure(bg="#f7f9fc")

    tk.Label(win, text="Manage Students", font=("Helvetica", 16, "bold"), bg="#2c3e50", fg="white").pack(fill="x")

    form = tk.Frame(win, bg="#f7f9fc")
    form.pack(pady=10)

    fields = [
        ("Roll No", "roll_no"),
        ("First Name", "first_name"),
        ("Last Name", "last_name"),
        ("Gender", "gender"),
        ("Date of Birth (YYYY-MM-DD)", "date_of_birth"),
        ("Email", "email"),
        ("Phone", "phone"),
        ("Address", "address"),
        ("Department", "department"),
        ("Semester", "semester")
    ]

    entries = {}
    for i, (label, col) in enumerate(fields):
        tk.Label(form, text=label, bg="#f7f9fc").grid(row=i, column=0, sticky="w", pady=4)
        e = tk.Entry(form, width=40)
        e.grid(row=i, column=1, pady=4, padx=8)
        entries[col] = e

    cols = [c for _, c in fields]
    tree = ttk.Treeview(win, columns=cols, show="headings")
    for label, col in fields:
        tree.heading(col, text=label)
        tree.column(col, width=120)
    tree.pack(expand=True, fill="both")

    def load_data():
        tree.delete(*tree.get_children())
        cur = conn.cursor()
        cur.execute("""
            SELECT roll_no, first_name, last_name, gender,
                   TO_CHAR(date_of_birth,'YYYY-MM-DD'),
                   email, phone, address, department, semester
            FROM students
        """)
        for row in cur:
            tree.insert("", "end", values=row)
        cur.close()

    def add_student():
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO students
            (roll_no, first_name, last_name, gender, date_of_birth, email, phone, address, department, semester)
            VALUES (:1, :2, :3, :4, TO_DATE(:5,'YYYY-MM-DD'), :6, :7, :8, :9, :10)
        """, tuple(entries[c].get() for c in cols))
        conn.commit(); cur.close(); load_data(); messagebox.showinfo("Success", "Student added!")

    def update_student():
        cur = conn.cursor()
        cur.execute("""
            UPDATE students SET
                first_name=:2, last_name=:3, gender=:4,
                date_of_birth=TO_DATE(:5,'YYYY-MM-DD'),
                email=:6, phone=:7, address=:8, department=:9, semester=:10
            WHERE roll_no=:1
        """, tuple(entries[c].get() for c in cols))
        conn.commit(); cur.close(); load_data(); messagebox.showinfo("Success", "Student updated!")

    def delete_student():
        cur = conn.cursor()
        cur.execute("DELETE FROM students WHERE roll_no=:1", (entries["roll_no"].get(),))
        conn.commit(); cur.close(); load_data(); messagebox.showinfo("Success", "Student deleted!")

    def search_student():
        tree.delete(*tree.get_children())
        cur = conn.cursor()
        cur.execute("""
            SELECT roll_no, first_name, last_name, gender,
                   TO_CHAR(date_of_birth,'YYYY-MM-DD'),
                   email, phone, address, department, semester
            FROM students WHERE roll_no=:1
        """, (entries["roll_no"].get(),))
        for row in cur:
            tree.insert("", "end", values=row)
        cur.close()

    btn_frame = tk.Frame(win, bg="#f7f9fc"); btn_frame.pack(pady=10)
    tk.Button(btn_frame, text="Add", bg="#27ae60", fg="white", command=add_student).grid(row=0, column=0, padx=5)
    tk.Button(btn_frame, text="Update", bg="#f39c12", fg="white", command=update_student).grid(row=0, column=1, padx=5)
    tk.Button(btn_frame, text="Delete", bg="#c0392b", fg="white", command=delete_student).grid(row=0, column=2, padx=5)
    tk.Button(btn_frame, text="Search", bg="#2980b9", fg="white", command=search_student).grid(row=0, column=3, padx=5)
    tk.Button(btn_frame, text="Refresh", bg="#34495e", fg="white", command=load_data).grid(row=0, column=4, padx=5)

    def on_select(_):
        sel = tree.selection()
        if not sel: return
        vals = tree.item(sel[0])["values"]
        for (label, col), v in zip(fields, vals):
            entries[col].delete(0, tk.END)
            entries[col].insert(0, "" if v is None else str(v))

    tree.bind("<<TreeviewSelect>>", on_select)
    load_data()
