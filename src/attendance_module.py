# src/attendance_module.py
import tkinter as tk
from tkinter import ttk, messagebox
import cx_Oracle
from db_config import DB_USER, DB_PASS, DB_DSN

def get_connection():
    return cx_Oracle.connect(DB_USER, DB_PASS, DB_DSN)

def build_tab(frame):
    global att_id_entry, att_student_entry, att_course_entry, att_status_entry, att_table
    form = tk.LabelFrame(frame, text="Attendance Form", bg="#f7f7f7")
    form.pack(fill="x", pady=10)
    tk.Label(form, text="Attendance ID:").grid(row=0, column=0, padx=8, pady=6)
    att_id_entry = tk.Entry(form); att_id_entry.grid(row=0, column=1, padx=8, pady=6)
    tk.Label(form, text="Student ID:").grid(row=1, column=0, padx=8, pady=6)
    att_student_entry = tk.Entry(form); att_student_entry.grid(row=1, column=1, padx=8, pady=6)
    tk.Label(form, text="Course ID:").grid(row=2, column=0, padx=8, pady=6)
    att_course_entry = tk.Entry(form); att_course_entry.grid(row=2, column=1, padx=8, pady=6)
    tk.Label(form, text="Status (Present/Absent):").grid(row=3, column=0, padx=8, pady=6)
    att_status_entry = tk.Entry(form); att_status_entry.grid(row=3, column=1, padx=8, pady=6)
    tk.Button(form, text="Add", command=add_att, bg="green", fg="white").grid(row=4, column=0, pady=8)
    tk.Button(form, text="Update", command=update_att, bg="orange", fg="white").grid(row=4, column=1, pady=8)
    tk.Button(form, text="Delete", command=delete_att, bg="red", fg="white").grid(row=4, column=2, pady=8)
    att_table = ttk.Treeview(frame, columns=("id","student","course","date","status"), show="headings")
    for h in ("id","student","course","date","status"): att_table.heading(h, text=h.title())
    att_table.pack(fill="both", expand=True, pady=8)
    att_table.bind("<<TreeviewSelect>>", on_select)
    list_att()

def add_att():
    con = get_connection(); cur = con.cursor()
    try:
        aid = int(att_id_entry.get().strip()); sid = int(att_student_entry.get().strip()); cid = int(att_course_entry.get().strip()); status = att_status_entry.get().strip()
        cur.execute("INSERT INTO attendance (attendance_id, student_id, course_id, status) VALUES (:a,:s,:c,:st)", dict(a=aid,s=sid,c=cid,st=status))
        con.commit(); messagebox.showinfo("Success","Attendance added"); list_att(); clear_form()
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        con.close()

def update_att():
    con = get_connection(); cur = con.cursor()
    try:
        aid = int(att_id_entry.get().strip()); sid = int(att_student_entry.get().strip()); cid = int(att_course_entry.get().strip()); status = att_status_entry.get().strip()
        cur.execute("UPDATE attendance SET student_id=:s, course_id=:c, status=:st WHERE attendance_id=:a", dict(s=sid,c=cid,st=status,a=aid))
        con.commit(); messagebox.showinfo("Success","Attendance updated"); list_att()
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        con.close()

def delete_att():
    con = get_connection(); cur = con.cursor()
    try:
        aid = int(att_id_entry.get().strip())
        if not messagebox.askyesno("Confirm","Delete attendance?"): return
        cur.execute("DELETE FROM attendance WHERE attendance_id=:a", dict(a=aid))
        con.commit(); messagebox.showinfo("Success","Attendance deleted"); list_att(); clear_form()
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        con.close()

def list_att():
    for r in att_table.get_children(): att_table.delete(r)
    con = get_connection(); cur = con.cursor()
    cur.execute("SELECT attendance_id, student_id, course_id, att_date, status FROM attendance ORDER BY attendance_id")
    for row in cur.fetchall(): att_table.insert("", "end", values=row)
    con.close()

def clear_form():
    att_id_entry.delete(0, tk.END); att_student_entry.delete(0, tk.END); att_course_entry.delete(0, tk.END); att_status_entry.delete(0, tk.END)

def on_select(event):
    sel = att_table.selection()
    if not sel: return
    vals = att_table.item(sel[0], "values")
    att_id_entry.delete(0, tk.END); att_id_entry.insert(0, vals[0])
    att_student_entry.delete(0, tk.END); att_student_entry.insert(0, vals[1])
    att_course_entry.delete(0, tk.END); att_course_entry.insert(0, vals[2])
    att_status_entry.delete(0, tk.END); att_status_entry.insert(0, vals[4])
