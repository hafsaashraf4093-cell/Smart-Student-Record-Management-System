# src/courses_module.py
import tkinter as tk
from tkinter import ttk, messagebox
import cx_Oracle
from db_config import DB_USER, DB_PASS, DB_DSN

def get_connection():
    return cx_Oracle.connect(DB_USER, DB_PASS, DB_DSN)

def build_tab(frame):
    global course_id_entry, course_name_entry, course_dept_entry, course_table
    form = tk.LabelFrame(frame, text="Course Form", bg="#f7f7f7")
    form.pack(fill="x", pady=10)
    tk.Label(form, text="Course ID:").grid(row=0, column=0, padx=8, pady=6)
    course_id_entry = tk.Entry(form); course_id_entry.grid(row=0, column=1, padx=8, pady=6)
    tk.Label(form, text="Course Name:").grid(row=1, column=0, padx=8, pady=6)
    course_name_entry = tk.Entry(form); course_name_entry.grid(row=1, column=1, padx=8, pady=6)
    tk.Label(form, text="Dept ID:").grid(row=2, column=0, padx=8, pady=6)
    course_dept_entry = tk.Entry(form); course_dept_entry.grid(row=2, column=1, padx=8, pady=6)
    tk.Button(form, text="Add", command=add_course, bg="green", fg="white").grid(row=3, column=0, pady=8)
    tk.Button(form, text="Update", command=update_course, bg="orange", fg="white").grid(row=3, column=1, pady=8)
    tk.Button(form, text="Delete", command=delete_course, bg="red", fg="white").grid(row=3, column=2, pady=8)
    course_table = ttk.Treeview(frame, columns=("id","name","dept"), show="headings")
    course_table.heading("id", text="Course ID"); course_table.heading("name", text="Course Name"); course_table.heading("dept", text="Dept ID")
    course_table.pack(fill="both", expand=True, pady=8)
    course_table.bind("<<TreeviewSelect>>", on_select)
    list_courses()

def add_course():
    con = get_connection(); cur = con.cursor()
    try:
        cid = int(course_id_entry.get().strip()); name = course_name_entry.get().strip(); did = int(course_dept_entry.get().strip())
        cur.execute("INSERT INTO courses (course_id, course_name, dept_id) VALUES (:c, :n, :d)", dict(c=cid, n=name, d=did))
        con.commit(); messagebox.showinfo("Success","Course added"); list_courses(); clear_form()
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        con.close()

def update_course():
    con = get_connection(); cur = con.cursor()
    try:
        cid = int(course_id_entry.get().strip()); name = course_name_entry.get().strip(); did = int(course_dept_entry.get().strip())
        cur.execute("UPDATE courses SET course_name=:n, dept_id=:d WHERE course_id=:c", dict(n=name, d=did, c=cid))
        con.commit(); messagebox.showinfo("Success","Course updated"); list_courses()
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        con.close()

def delete_course():
    con = get_connection(); cur = con.cursor()
    try:
        cid = int(course_id_entry.get().strip())
        if not messagebox.askyesno("Confirm","Delete course?"): return
        cur.execute("DELETE FROM courses WHERE course_id=:c", dict(c=cid))
        con.commit(); messagebox.showinfo("Success","Course deleted"); list_courses(); clear_form()
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        con.close()

def list_courses():
    for r in course_table.get_children(): course_table.delete(r)
    con = get_connection(); cur = con.cursor()
    cur.execute("SELECT course_id, course_name, dept_id FROM courses ORDER BY course_id")
    for row in cur.fetchall(): course_table.insert("", "end", values=row)
    con.close()

def clear_form():
    course_id_entry.delete(0, tk.END); course_name_entry.delete(0, tk.END); course_dept_entry.delete(0, tk.END)

def on_select(event):
    sel = course_table.selection()
    if not sel: return
    vals = course_table.item(sel[0], "values")
    course_id_entry.delete(0, tk.END); course_id_entry.insert(0, vals[0])
    course_name_entry.delete(0, tk.END); course_name_entry.insert(0, vals[1])
    course_dept_entry.delete(0, tk.END); course_dept_entry.insert(0, vals[2])
