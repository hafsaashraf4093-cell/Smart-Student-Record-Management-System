# src/dept_module.py
import tkinter as tk
from tkinter import ttk, messagebox
import cx_Oracle
from db_config import DB_USER, DB_PASS, DB_DSN

def get_connection():
    return cx_Oracle.connect(DB_USER, DB_PASS, DB_DSN)

def build_tab(frame):
    global dept_id_entry, dept_name_entry, dept_table
    form = tk.LabelFrame(frame, text="Department Form", bg="#f7f7f7")
    form.pack(fill="x", pady=10)
    tk.Label(form, text="Dept ID:").grid(row=0, column=0, padx=8, pady=6)
    dept_id_entry = tk.Entry(form); dept_id_entry.grid(row=0, column=1, padx=8, pady=6)
    tk.Label(form, text="Dept Name:").grid(row=1, column=0, padx=8, pady=6)
    dept_name_entry = tk.Entry(form); dept_name_entry.grid(row=1, column=1, padx=8, pady=6)
    tk.Button(form, text="Add", command=add_dept, bg="green", fg="white").grid(row=2, column=0, pady=8)
    tk.Button(form, text="Update", command=update_dept, bg="orange", fg="white").grid(row=2, column=1, pady=8)
    tk.Button(form, text="Delete", command=delete_dept, bg="red", fg="white").grid(row=2, column=2, pady=8)
    dept_table = ttk.Treeview(frame, columns=("id","name"), show="headings")
    dept_table.heading("id", text="Dept ID"); dept_table.heading("name", text="Dept Name")
    dept_table.pack(fill="both", expand=True, pady=8)
    dept_table.bind("<<TreeviewSelect>>", on_select)
    list_dept()

def add_dept():
    con = get_connection(); cur = con.cursor()
    try:
        did = int(dept_id_entry.get().strip()); name = dept_name_entry.get().strip()
        if not name: messagebox.showerror("Invalid", "Dept name required"); return
        cur.execute("INSERT INTO department (dept_id, dept_name) VALUES (:id, :name)", dict(id=did, name=name))
        con.commit(); messagebox.showinfo("Success","Department added"); list_dept(); clear_form()
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        con.close()

def update_dept():
    con = get_connection(); cur = con.cursor()
    try:
        did = int(dept_id_entry.get().strip()); name = dept_name_entry.get().strip()
        cur.execute("UPDATE department SET dept_name=:name WHERE dept_id=:id", dict(name=name, id=did))
        con.commit(); messagebox.showinfo("Success","Department updated"); list_dept()
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        con.close()

def delete_dept():
    con = get_connection(); cur = con.cursor()
    try:
        did = int(dept_id_entry.get().strip())
        if not messagebox.askyesno("Confirm","Delete department?"): return
        cur.execute("DELETE FROM department WHERE dept_id=:id", dict(id=did))
        con.commit(); messagebox.showinfo("Success","Department deleted"); list_dept(); clear_form()
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        con.close()

def list_dept():
    for r in dept_table.get_children(): dept_table.delete(r)
    con = get_connection(); cur = con.cursor()
    cur.execute("SELECT dept_id, dept_name FROM department ORDER BY dept_id")
    for row in cur.fetchall(): dept_table.insert("", "end", values=row)
    con.close()

def clear_form():
    dept_id_entry.delete(0, tk.END); dept_name_entry.delete(0, tk.END)

def on_select(event):
    sel = dept_table.selection()
    if not sel: return
    vals = dept_table.item(sel[0], "values")
    dept_id_entry.delete(0, tk.END); dept_id_entry.insert(0, vals[0])
    dept_name_entry.delete(0, tk.END); dept_name_entry.insert(0, vals[1])
