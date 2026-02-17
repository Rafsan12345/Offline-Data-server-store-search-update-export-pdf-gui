import sqlite3
import tkinter as tk
from tkinter import messagebox, filedialog
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# ================= DATABASE =================
conn = sqlite3.connect("messages.db")
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            message TEXT
            )""")
conn.commit()

# ================= FUNCTIONS =================
def save_data():
    id_val = entry_id.get()
    msg_val = text_message.get("1.0", tk.END).strip()
    if id_val and msg_val:
        try:
            c.execute("INSERT INTO messages (id, message) VALUES (?, ?)", (id_val, msg_val))
            conn.commit()
            messagebox.showinfo("Success", "Record saved successfully!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "ID already exists! Use update instead.")
    else:
        messagebox.showwarning("Input Error", "Please enter both ID and Message")

def search_data():
    id_val = entry_id.get()
    if id_val:
        c.execute("SELECT message FROM messages WHERE id=?", (id_val,))
        record = c.fetchone()
        if record:
            # নতুন উইন্ডো তৈরি
            popup = tk.Toplevel(root)
            popup.title(f"Message for ID: {id_val}")
            popup.geometry("400x200")
            tk.Label(popup, text=f"ID: {id_val}", font=("Arial", 12, "bold")).pack(pady=10)
            msg_box = tk.Text(popup, font=("Arial", 12), height=5, width=40)
            msg_box.pack(pady=5)
            msg_box.insert(tk.END, record[0])
            msg_box.config(state=tk.DISABLED)  # শুধু দেখানোর জন্য
            tk.Button(popup, text="Close", command=popup.destroy, bg="#f44336", fg="white").pack(pady=10)
        else:
            messagebox.showinfo("Not Found", "No record found with this ID")
    else:
        messagebox.showwarning("Input Error", "Please enter an ID to search")

def update_data():
    id_val = entry_id.get()
    msg_val = text_message.get("1.0", tk.END).strip()
    if id_val and msg_val:
        c.execute("UPDATE messages SET message=? WHERE id=?", (msg_val, id_val))
        if c.rowcount == 0:
            messagebox.showinfo("Not Found", "No record found to update")
        else:
            conn.commit()
            messagebox.showinfo("Success", "Record updated successfully")
    else:
        messagebox.showwarning("Input Error", "Please enter both ID and Message")

def export_pdf():
    file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files","*.pdf")])
    if file_path:
        c.execute("SELECT * FROM messages")
        records = c.fetchall()
        if records:
            pdf = canvas.Canvas(file_path, pagesize=letter)
            pdf.setTitle("Messages Record")
            pdf.setFont("Helvetica", 12)
            y = 750
            pdf.drawString(50, 780, "ID")
            pdf.drawString(150, 780, "Message")
            for rec in records:
                pdf.drawString(50, y, rec[0])
                pdf.drawString(150, y, rec[1])
                y -= 20
                if y < 50:
                    pdf.showPage()
                    y = 750
            pdf.save()
            messagebox.showinfo("Success", f"PDF saved at {file_path}")
        else:
            messagebox.showinfo("No Data", "No records found to export")

# ================= TKINTER GUI =================
root = tk.Tk()
root.title("Message Manager")
root.geometry("500x400")
root.resizable(False, False)

# ---- Labels ----
tk.Label(root, text="ID:", font=("Arial", 12)).place(x=20, y=20)
tk.Label(root, text="Message:", font=("Arial", 12)).place(x=20, y=60)

# ---- Entries ----
entry_id = tk.Entry(root, font=("Arial", 12))
entry_id.place(x=100, y=20, width=150)

text_message = tk.Text(root, font=("Arial", 12), height=8, width=40)
text_message.place(x=100, y=60)

# ---- Buttons ----
btn_save = tk.Button(root, text="Save", font=("Arial", 12), command=save_data, bg="#4CAF50", fg="white")
btn_save.place(x=50, y=250, width=80)

btn_search = tk.Button(root, text="Search", font=("Arial", 12), command=search_data, bg="#2196F3", fg="white")
btn_search.place(x=150, y=250, width=80)

btn_update = tk.Button(root, text="Update", font=("Arial", 12), command=update_data, bg="#FFC107", fg="black")
btn_update.place(x=250, y=250, width=80)

btn_pdf = tk.Button(root, text="Export PDF", font=("Arial", 12), command=export_pdf, bg="#9C27B0", fg="white")
btn_pdf.place(x=350, y=250, width=100)

root.mainloop()
