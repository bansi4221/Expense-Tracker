import tkinter as tk
from tkinter import messagebox
import re
import mysql.connector
import smtplib
import random
import mainrendom
import datetime
import mysql.connector
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg



# Establish a MySQL connection
def connect_to_database():
    return mysql.connector.connect(
        host="localhost",        # Replace with your MySQL server host
        user="root",             # Replace with your MySQL username
        password="",     # Replace with your MySQL password
        database="user_management"
    )

# Toggle Password Visibility
def toggle_password_visibility(entry, checkbox_var):
    if entry.cget('show') == '*':
        entry.config(show='')
    else:
        entry.config(show='*')

# Center the window on the screen
def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")
    
# Login Function
def login():
    username = username_entry.get()
    password = password_entry.get()
    if username and password:
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        result = cursor.fetchone()
        if result:
            messagebox.showinfo("Login Info", f"Welcome, {username}!")
            username_entry.delete(0, tk.END)
            password_entry.delete(0, tk.END)
            root.withdraw()
            mainrendom.open_main_form(username, on_logout=root.deiconify)
        else:
            cursor.execute("SELECT * FROM client WHERE username = %s AND password = %s", (username, password))
            client_result = cursor.fetchone()
            if client_result:
                messagebox.showinfo("Login Info", "Client Login Successful!")
                open_client_panel()
            else:
                messagebox.showerror("Login Error", "Invalid username or password.")
        conn.close()
    else:
        messagebox.showwarning("Login Warning", "Please enter both username and password.")
        # Clear the username and password fields
    username_entry.delete(0, tk.END)
    password_entry.delete(0, tk.END)


# Sign-In Form
def open_sign_in_form():
    sign_in_window = tk.Toplevel(root)
    sign_in_window.title("Sign-In Form")
    sign_in_window.geometry("350x250")
    
    tk.Label(sign_in_window, text="Username:").grid(row=0, column=0, padx=10, pady=10)
    username_entry = tk.Entry(sign_in_window, width=30)
    username_entry.grid(row=0, column=1)
    
    tk.Label(sign_in_window, text="Password:").grid(row=1, column=0, padx=10, pady=10)
    password_entry = tk.Entry(sign_in_window, width=30, show='*')
    password_entry.grid(row=1, column=1)
    
    show_password_var = tk.BooleanVar()
    show_password_checkbox = tk.Checkbutton(sign_in_window, text="Show Password", variable=show_password_var, command=lambda: toggle_password_visibility(password_entry, show_password_var))
    show_password_checkbox.grid(row=2, columnspan=2)
    
    def store_client():
        username = username_entry.get()
        password = password_entry.get()
        
        if not username or not password:
            messagebox.showwarning("Input Error", "All fields are required!")
            return
        
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS client (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), password VARCHAR(255))")
        query = "INSERT INTO client (username, password) VALUES (%s, %s)"
        cursor.execute(query, (username, password))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Sign-In Successful!")
        sign_in_window.destroy()
        root.deiconify()
    
    submit_button = tk.Button(sign_in_window, text="Submit", command=store_client, bg="#6495ED", fg="white")
    submit_button.grid(row=3, columnspan=2, pady=10)
    
    def back_to_login():
        sign_in_window.destroy()
        root.deiconify()
    
    back_to_login_label = tk.Label(sign_in_window, text="Back to Login", fg="blue", cursor="hand2")
    back_to_login_label.grid(row=4, columnspan=2)
    back_to_login_label.bind("<Button-1>", lambda e: back_to_login())
# Open Client Panel
def open_client_panel():
    client_panel = tk.Toplevel(root)
    client_panel.title("Client Panel")
    client_panel.geometry("400x200")
    
    tk.Label(client_panel, text="Date (YYYY-MM-DD):").grid(row=0, column=0, padx=10, pady=10)
    date_entry = tk.Entry(client_panel, width=30)
    date_entry.grid(row=0, column=1)
    date_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
    
    def generate_report():
        date_value = date_entry.get().strip()

        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_value):
            messagebox.showerror("Invalid Input", "Enter a valid date in yyyy-mm-dd format.")
            return

        year, month, _ = date_value.split("-")
        menu_items = {"Drink": "drink", "Electronic": "electronic", "Bills": "bills", "Grocery": "grocery"}
        
        total_expenses = {}
        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="", database="expense_tracker3")
            cursor = conn.cursor()
            
            for category, table_name in menu_items.items():
                query = f"SELECT SUM(unit_amount) FROM {table_name} WHERE YEAR(expense_date) = %s AND MONTH(expense_date) = %s"
                cursor.execute(query, (year, month))
                result = cursor.fetchone()[0]
                total_expenses[category] = result if result else 0  # Default to 0 if no data
            
            conn.close()
            
            if all(value == 0 for value in total_expenses.values()):
                messagebox.showinfo("No Data", "No records found for the selected month.")
                return
            
            fig, ax = plt.subplots(figsize=(10, 7))
            ax.bar(total_expenses.keys(), total_expenses.values(), color=['blue', 'red', 'green', 'orange'])
            
            ax.set_title(f"Total Monthly Expenses - {year}-{month}", fontsize=16, fontweight='bold')
            ax.set_xlabel("Categories", fontsize=12)
            ax.set_ylabel("Month Expense", fontsize=12)
            ax.set_xticklabels(total_expenses.keys(), rotation=60, ha="right")
            
            for i, v in enumerate(total_expenses.values()):
                ax.text(i, v + 10, f"{v}", ha='center', fontsize=12, fontweight='bold')
            
            graph_window = tk.Toplevel(client_panel)
            graph_window.title("Graph Report")

                        # Centering the graph window
            screen_width = graph_window.winfo_screenwidth()
            screen_height = graph_window.winfo_screenheight()
            width, height = 700, 600  # Set the dimensions of the graph window
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
            graph_window.geometry(f"{width}x{height}+{x}+{y}")

            
            canvas = FigureCanvasTkAgg(fig, master=graph_window)
            canvas.draw()
            canvas.get_tk_widget().pack()
        
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

    
    report_button = tk.Button(client_panel, text="Report", command=generate_report, bg="#6495ED", fg="white")
    report_button.grid(row=1, columnspan=2, pady=10)



# Redirect to Registration Form
def open_registration_form():
    root.withdraw()
    registration_form()

# Registration Form
def registration_form():
    reg_window = tk.Toplevel(root)
    reg_window.title("Registration Form")
    center_window(reg_window, 400, 450)
    reg_window.resizable(False, False)
    
     #Bring the window to the front
    reg_window.lift()
    reg_window.focus_force()

    
    tk.Label(reg_window, text="Registration Form", font=("Helvetica", 16, "bold")).pack(pady=(10, 20))

    tk.Label(reg_window, text="Name:").pack(pady=(10, 5))
    name_entry = tk.Entry(reg_window, width=30)
    name_entry.pack()

    tk.Label(reg_window, text="Mobile Number:").pack(pady=(10, 5))
    mobile_entry = tk.Entry(reg_window, width=30)
    mobile_entry.pack()

    tk.Label(reg_window, text="Email:").pack(pady=(10, 5))
    email_entry = tk.Entry(reg_window, width=30)
    email_entry.pack()

    tk.Label(reg_window, text="Username:").pack(pady=(10, 5))
    username_entry_reg = tk.Entry(reg_window, width=30)
    username_entry_reg.pack()

    tk.Label(reg_window, text="Password:").pack(pady=(10, 5))
    password_entry_reg = tk.Entry(reg_window, width=30, show='*')
    password_entry_reg.pack()

    show_password_var_reg = tk.BooleanVar()
    show_password_checkbox = tk.Checkbutton(
        reg_window, text="Show Password",
        variable=show_password_var_reg,
        command=lambda: toggle_password_visibility(password_entry_reg, show_password_var_reg)
    )
    show_password_checkbox.pack(pady=5)

    def register_user():
        name = name_entry.get()
        mobile = mobile_entry.get()
        email = email_entry.get()
        username = username_entry_reg.get()
        password = password_entry_reg.get()

        if not name:
            messagebox.showwarning("Input Error", "Name cannot be empty.")
            return

        if not mobile.isdigit() or len(mobile) != 10:
            messagebox.showwarning("Input Error", "Mobile number must be exactly 10 digits.")
            return

        email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
        if not re.match(email_pattern, email):
            messagebox.showwarning("Input Error", "Invalid email address.")
            return

        if not re.search(r"[A-Za-z]", username) or not re.search(r"[0-9]", username):
            messagebox.showwarning("Input Error", "Username must contain both letters and digits.")
            return

        if len(password) < 8:
            messagebox.showwarning("Input Error", "Password must be at least 8 characters long.")
            return

        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            query = "INSERT INTO users (name, mobile, email, username, password) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(query, (name, mobile, email, username, password))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Registration is successful!")
            reg_window.destroy()
            root.deiconify()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

    tk.Button(reg_window, text="Register", command=register_user, bg="#6495ED", fg="white", borderwidth=0, width="14").pack(pady=(10, 20))

    def back_to_login():
        reg_window.destroy()
        root.deiconify()

    back_to_login_label = tk.Label(reg_window, text="Back to Login", fg="blue", cursor="hand2")
    back_to_login_label.pack()
    back_to_login_label.bind("<Button-1>", lambda e: back_to_login())

root = tk.Tk()
root.title("Login Form")
center_window(root, 400, 350)
root.resizable(False, False)

login_label = tk.Label(root, text="Login", font=("Helvetica", 16, "bold"))
login_label.pack(pady=(10, 20))

username_label = tk.Label(root, text="Username:")
username_label.pack(pady=(20, 5))
username_entry = tk.Entry(root, width=30)
username_entry.pack()

password_label = tk.Label(root, text="Password:")
password_label.pack(pady=(10, 5))
password_entry = tk.Entry(root, width=30, show='*')
password_entry.pack()

show_password_var = tk.BooleanVar()
show_password_checkbox = tk.Checkbutton(root, text="Show Password", variable=show_password_var, command=lambda: toggle_password_visibility(password_entry, show_password_var))
show_password_checkbox.pack(pady=5)

login_button = tk.Button(root, text="Login", command=login, bg="#6495ED", fg="white", borderwidth=0, width=13)
login_button.pack(pady=(10, 5))

register_button = tk.Button(root, text="Register", command=open_registration_form, bg="#6495ED", fg="white", borderwidth=0, width=15)
register_button.pack(pady=(10, 5))


# Toggle Password Visibility
def toggle_password_visibility(entry, checkbox_var):
    if entry.cget('show') == '*':
        entry.config(show='')
    else:
        entry.config(show='*')

# Send OTP via Email
def send_otp(email):
    global otp
    otp = str(random.randint(100000, 999999))
    sender_email = ""  # Replace with your email
    sender_password = ""  # Replace with your Google App Password
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        message = f"Subject: Password Reset OTP\n\nYour OTP is {otp}"
        server.sendmail(sender_email, email, message)
        server.quit()
        messagebox.showinfo("OTP Sent", "OTP has been sent to your email.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to send OTP: {e}")

# Verify OTP
def verify_otp(otp_entry, verify_window):
    if otp_entry.get() == otp:
        verify_window.destroy()
        reset_password_form()
    else:
        messagebox.showerror("Invalid OTP", "The OTP you entered is incorrect.")

# Open Reset Password Form
def reset_password_form():
    reset_window = tk.Toplevel(root)
    reset_window.title("Reset Password")
    reset_window.geometry("400x300")
    
    tk.Label(reset_window, text="New Password:").pack(pady=(10, 5))
    new_password_entry = tk.Entry(reset_window, width=30, show='*')
    new_password_entry.pack()
    
    tk.Label(reset_window, text="Confirm Password:").pack(pady=(10, 5))
    confirm_password_entry = tk.Entry(reset_window, width=30, show='*')
    confirm_password_entry.pack()
    
    show_password_var = tk.BooleanVar()
    show_password_checkbox = tk.Checkbutton(reset_window, text="Show Password", variable=show_password_var, command=lambda: toggle_password_visibility(new_password_entry,confirm_password_entry))
    show_password_checkbox.pack()
    
    def update_password():
        new_password = new_password_entry.get()
        confirm_password = confirm_password_entry.get()
        if len(new_password) != 8:
            messagebox.showerror("Error", "Password must be exactly 8 characters long.")
            return
        if new_password == confirm_password:
            try:
                conn = connect_to_database()
                cursor = conn.cursor()
                query = "UPDATE users SET password = %s WHERE email = %s"
                cursor.execute(query, (new_password, user_email))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Password reset successfully!")
                reset_window.destroy()
                forgot_window.destroy()
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Error: {err}")
        else:
            messagebox.showerror("Error", "Passwords do not match.")
    
    tk.Button(reset_window, text="Reset Password", command=update_password, bg="#6495ED", fg="white").pack(pady=(10, 20))

# Open Forgot Password Form
def forgot_password_form():
    global forgot_window
    forgot_window = tk.Toplevel(root)
    forgot_window.title("Forgot Password")
    forgot_window.geometry("350x200")
    
    tk.Label(forgot_window, text="Enter your Email:").pack(pady=(10, 5))
    email_entry = tk.Entry(forgot_window, width=30)
    email_entry.pack()
    
    def send_otp_and_proceed():
        global user_email,verify_window
        user_email = email_entry.get()
        send_otp(user_email)
        
        verify_window = tk.Toplevel(forgot_window)
        verify_window.title("Verify OTP")
        verify_window.geometry("300x200")
        
        tk.Label(verify_window, text="Enter OTP:").pack(pady=(10, 5))
        otp_entry = tk.Entry(verify_window, width=20)
        otp_entry.pack()
        
        tk.Button(verify_window, text="Verify", command=lambda: verify_otp(otp_entry, verify_window), bg="#6495ED", fg="white").pack(pady=(10, 20))
    
    tk.Button(forgot_window, text="Send", command=send_otp_and_proceed, bg="#6495ED", fg="white").pack(pady=(10, 20))


forgot_password_label = tk.Label(root, text="Forgot Password?", fg="blue", cursor="hand2")
forgot_password_label.pack()
forgot_password_label.bind("<Button-1>", lambda e: forgot_password_form())

sign_in_button = tk.Button(root, text="Sign-In", command=open_sign_in_form, bg="#6495ED", fg="white", borderwidth=0, width=15)
sign_in_button.pack(pady=(10, 5))

root.mainloop()
