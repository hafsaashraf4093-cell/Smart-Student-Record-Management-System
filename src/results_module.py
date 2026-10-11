# src/results_module.py
import tkinter as tk
from tkinter import ttk, messagebox
import cx_Oracle
from db_config import DB_USER, DB_PASS, DB_DSN

def get_connection():
    return cx_Oracle.connect(DB_USER, DB_PASS, DB_DSN)

def build_tab(frame):
    global res_id_entry, res_student_entry, res_course_entry, res_grade_entry, res_table
    form = tk.LabelFrame(frame, text="Results Form", bg="#f7f7f7")
    form.pack(fill="x", pady=10)
    tk.Label(form, text="Result ID:").grid(row=0, column=0, padx=8, pady=6)
    res_id_entry = tk.Entry(form); res_id_entry.grid(row=0, column=1, padx=8, pady=6)
    tk.Label(form, text="Student ID:").grid(row=1, column=0, padx=8, pady=6)
    res_student_entry = tk.Entry(form); res_student_entry.grid(row=1, column=1, padx=8, pady=6)
    tk.Label(form, text="Course ID:").grid(row=2, column=0, padx=8, pady=6)
    res_course_entry = tk.Entry(form); res_course_entry.grid(row=2, column=1, padx=8, pady=6)
    tk.Label(form, text="Grade:").grid(row=3, column=0, padx=8, pady=6)
    res_grade_entry = tk.Entry(form); res_grade_entry.grid(row=3, column=1, padx=8, pady=6)
    tk.Button(form, text="Add", command=add_result, bg="green", fg="white").grid(row=4, column=0, pady=8)
    tk.Button(form, text="Update", command=update_result, bg="orange", fg="white").grid(row=4, column=1, pady=8)
    tk.Button(form, text="Delete", command=delete_result, bg="red", fg="white").grid(row=4, column=2, pady=8)
    res_table = ttk.Treeview(frame, columns=("id","student","course","grade"), show="headings")
    for h in ("id","student","course","grade"): res_table.heading(h, text=h.title())
    res_table.pack(fill="both", expand=True, pady=8)
    res_table.bind("<<TreeviewSelect>>", on_select)
    list_results()

def add_result():
    con = get_connection(); cur = con.cursor()
    try:
        rid = int(res_id_entry.get().strip()); sid = int(res_student_entry.get().strip()); cid = int(res_course_entry.get().strip()); grade = res_grade_entry.get().strip()
        cur.execute("INSERT INTO results (result_id, student_id, course_id, grade) VALUES (:r,:s,:c,:g)", dict(r=rid,s=sid,c=cid,g=grade))
        con.commit(); messagebox.showinfo("Success","Result added"); list_results(); clear_form()
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        con.close()

def update_result():
    con = get_connection(); cur = con.cursor()
    try:
        rid = int(res_id_entry.get().strip()); sid = int(res_student_entry.get().strip()); cid = int(res_course_entry.get().strip()); grade = res_grade_entry.get().strip()
        cur.execute("UPDATE results SET student_id=:s, course_id=:c, grade=:g WHERE result_id=:r", dict(s=sid,c=cid,g=grade,r=rid))
        con.commit(); messagebox.showinfo("Success","Result updated"); list_results()
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        con.close()

def delete_result():
    con = get_connection(); cur = con.cursor()
    try:
        rid = int(res_id_entry.get().strip())
        if not messagebox.askyesno("Confirm","Delete result?"): return
        cur.execute("DELETE FROM results WHERE result_id=:r", dict(r=rid))
        con.commit(); messagebox.showinfo("Success","Result deleted"); list_results(); clear_form()
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        con.close()

def list_results():
    for r in res_table.get_children(): res_table.delete(r)
    con = get_connection(); cur = con.cursor()
    cur.execute("SELECT result_id, student_id, course_id, grade FROM results ORDER BY result_id")
    for row in cur.fetchall(): res_table.insert("", "end", values=row)
    con.close()

def clear_form():
    res_id_entry.delete(0, tk.END); res_student_entry.delete(0, tk.END); res_course_entry.delete(0, tk.END); res_grade_entry.delete(0, tk.END)

def on_select(event):
    sel = res_table.selection()
    if not sel: return
    vals = res_table.item(sel[0], "values")
    res_id_entry.delete(0, tk.END); res_id_entry.insert(0, vals[0])
    res_student_entry.delete(0, tk.END); res_student_entry.insert(0, vals[1])
    res_course_entry.delete(0, tk.END); res_course_entry.insert(0, vals[2])
    res_grade_entry.delete(0, tk.END); res_grade_entry.insert(0, vals[3])
