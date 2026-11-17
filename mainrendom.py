
"""
Expense Tracker - Main application
Database: expense_tracker3
Tables: drink, electronic, bills, grocery
Required columns: id, item_name, quantity, unit_amount, expense_date
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date, datetime
import csv
import mysql.connector
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "expense_tracker3"
}

CATEGORIES = {
    "Drinks": "drink",
    "Electronics": "electronic",
    "Bills": "bills",
    "Grocery": "grocery",
}

BG = "#F3F6FB"
NAVY = "#172B4D"
BLUE = "#3478F6"
WHITE = "#FFFFFF"
TEXT = "#243247"
MUTED = "#718096"


def connect_to_database():
    return mysql.connector.connect(**DB_CONFIG)


def money(value):
    return f"₹{float(value or 0):,.2f}"


def open_main_form(username="User", on_logout=None):

    app = tk.Tk()
    app.title("Expense Tracker | Dashboard")
    app.geometry("1280x800")
    app.minsize(1050, 680)
    app.configure(bg=BG)

    selected_category = tk.StringVar(value="All categories")
    selected_record_id = tk.IntVar(value=0)
    current_rows = []

    style = ttk.Style()
    style.theme_use("clam")

    style.configure(
        "Treeview",
        background="white",
        fieldbackground="white",
        foreground=TEXT,
        rowheight=30,
        font=("Segoe UI", 9)
    )

    style.configure(
        "Treeview.Heading",
        background="#E8EEF8",
        foreground=NAVY,
        font=("Segoe UI", 9, "bold"),
        relief="flat"
    )

    style.map(
        "Treeview",
        background=[("selected", "#D9E7FF")],
        foreground=[("selected", NAVY)]
    )

    style.configure("TCombobox", padding=6)

    def close_app():
        app.destroy()
        if on_logout:
            on_logout()

    def month_date_range(month):
        first_day = datetime.strptime(month, "%Y-%m").date()

        if first_day.month == 12:
            next_month = date(first_day.year + 1, 1, 1)
        else:
            next_month = date(
                first_day.year,
                first_day.month + 1,
                1
            )

        return first_day, next_month

    def query_total(table, month=None):
        conn = connect_to_database()
        cur = conn.cursor()

        try:
            if month:
                first_day, next_month = month_date_range(month)

                cur.execute(
                    f"SELECT COALESCE(SUM(unit_amount), 0) "
                    f"FROM {table} "
                    "WHERE expense_date >= %s "
                    "AND expense_date < %s",
                    (first_day, next_month)
                )
            else:
                cur.execute(
                    f"SELECT COALESCE(SUM(unit_amount), 0) "
                    f"FROM {table}"
                )

            return float(cur.fetchone()[0] or 0)

        finally:
            cur.close()
            conn.close()

    def all_totals(month=None):
        totals = {}

        for label, table in CATEGORIES.items():
            totals[label] = query_total(table, month)

        return totals

    # Header
    header = tk.Frame(app, bg=NAVY, height=76)
    header.pack(fill="x")
    header.pack_propagate(False)

    tk.Label(
        header,
        text="₹  EXPENSE TRACKER",
        bg=NAVY,
        fg="white",
        font=("Segoe UI", 18, "bold")
    ).pack(side="left", padx=28)

    tk.Label(
        header,
        text=f"Signed in as  {username}",
        bg=NAVY,
        fg="#D8E4F5",
        font=("Segoe UI", 10)
    ).pack(side="right", padx=22)

    # Main body
    body = tk.Frame(app, bg=BG)
    body.pack(fill="both", expand=True)

    sidebar = tk.Frame(body, bg=WHITE, width=205)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    content = tk.Frame(body, bg=BG, padx=24, pady=20)
    content.pack(side="left", fill="both", expand=True)

    page_title = tk.Label(
        content,
        text="Overview",
        bg=BG,
        fg=NAVY,
        font=("Segoe UI", 22, "bold")
    )
    page_title.pack(anchor="w")

    page_subtitle = tk.Label(
        content,
        text="A clear view of your spending.",
        bg=BG,
        fg=MUTED,
        font=("Segoe UI", 10)
    )
    page_subtitle.pack(anchor="w", pady=(2, 18))

    page = tk.Frame(content, bg=BG)
    page.pack(fill="both", expand=True)

    def clear_page():
        for child in page.winfo_children():
            child.destroy()

    def nav_button(label, command):
        tk.Button(
            sidebar,
            text=label,
            command=command,
            anchor="w",
            bg=WHITE,
            fg=TEXT,
            activebackground="#EAF1FF",
            activeforeground=BLUE,
            relief="flat",
            bd=0,
            font=("Segoe UI", 10, "bold"),
            padx=22,
            pady=14,
            cursor="hand2"
        ).pack(fill="x", padx=9, pady=3)

    def set_title(title, subtitle):
        page_title.config(text=title)
        page_subtitle.config(text=subtitle)

    # Dashboard
    def show_dashboard():

        set_title("Overview", "A clear view of your spending.")
        clear_page()

        month = date.today().strftime("%Y-%m")

        try:
            totals = all_totals(month)
            total = sum(totals.values())

            count_conn = connect_to_database()
            cur = count_conn.cursor()
            count = 0

            for table in CATEGORIES.values():
                first_day, next_month = month_date_range(month)

                cur.execute(
                    f"SELECT COUNT(*) FROM {table} "
                    "WHERE expense_date >= %s "
                    "AND expense_date < %s",
                    (first_day, next_month)
                )

                count += cur.fetchone()[0]

            cur.close()
            count_conn.close()

        except mysql.connector.Error as err:
            messagebox.showerror("Database error", str(err))
            return

        cards = tk.Frame(page, bg=BG)
        cards.pack(fill="x")

        card_data = [
            ("THIS MONTH", money(total)),
            ("TRANSACTIONS", str(count)),
            (
                "CATEGORIES USED",
                str(sum(1 for v in totals.values() if v > 0))
            )
        ]

        for label, value in card_data:
            card = tk.Frame(
                cards,
                bg=WHITE,
                padx=20,
                pady=18,
                highlightbackground="#E1E7F0",
                highlightthickness=1
            )
            card.pack(
                side="left",
                fill="both",
                expand=True,
                padx=(0, 12)
            )

            tk.Label(
                card,
                text=label,
                bg=WHITE,
                fg=MUTED,
                font=("Segoe UI", 9, "bold")
            ).pack(anchor="w")

            tk.Label(
                card,
                text=value,
                bg=WHITE,
                fg=NAVY,
                font=("Segoe UI", 20, "bold")
            ).pack(anchor="w", pady=(8, 0))

        lower = tk.Frame(page, bg=BG)
        lower.pack(fill="both", expand=True, pady=(18, 0))

        chart_card = tk.Frame(
            lower,
            bg=WHITE,
            padx=14,
            pady=12,
            highlightbackground="#E1E7F0",
            highlightthickness=1
        )
        chart_card.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 12)
        )

        tk.Label(
            chart_card,
            text="Monthly spending by category",
            bg=WHITE,
            fg=NAVY,
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w")

        fig, ax = plt.subplots(figsize=(6.2, 3.6), dpi=90)

        names = list(totals.keys())
        values = list(totals.values())

        ax.bar(names, values)
        ax.set_ylabel("Amount (₹)")
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(axis="x", rotation=15)

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=chart_card)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)

        side = tk.Frame(
            lower,
            bg=WHITE,
            padx=18,
            pady=16,
            highlightbackground="#E1E7F0",
            highlightthickness=1
        )
        side.pack(side="right", fill="y")

        tk.Label(
            side,
            text="Category summary",
            bg=WHITE,
            fg=NAVY,
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", pady=(0, 12))

        for name, amount in totals.items():
            line = tk.Frame(side, bg=WHITE)
            line.pack(fill="x", pady=8)

            tk.Label(
                line,
                text=name,
                bg=WHITE,
                fg=TEXT,
                font=("Segoe UI", 10)
            ).pack(side="left")

            tk.Label(
                line,
                text=money(amount),
                bg=WHITE,
                fg=NAVY,
                font=("Segoe UI", 10, "bold")
            ).pack(side="right")

        tk.Button(
            side,
            text="View expenses",
            command=show_expenses,
            bg=BLUE,
            fg="white",
            relief="flat",
            padx=16,
            pady=9
        ).pack(fill="x", pady=(20, 0))

    # Expense management
    def show_expenses(category=None):

        set_title(
            "Expenses",
            "Add, update, search and manage your expense records."
        )

        clear_page()
        selected_record_id.set(0)

        selected_category.set(category or "All categories")

        # Top filter toolbar
        toolbar = tk.Frame(page, bg=BG)
        toolbar.pack(fill="x", pady=(0, 12))

        tk.Label(
            toolbar,
            text="Category",
            bg=BG,
            fg=TEXT
        ).pack(side="left", padx=(0, 8))

        category_box = ttk.Combobox(
            toolbar,
            textvariable=selected_category,
            values=["All categories"] + list(CATEGORIES.keys()),
            state="readonly",
            width=19
        )
        category_box.pack(side="left")

        tk.Label(
            toolbar,
            text="Search item",
            bg=BG,
            fg=TEXT
        ).pack(side="left", padx=(18, 8))

        search_var = tk.StringVar()

        search_entry = ttk.Entry(
            toolbar,
            textvariable=search_var,
            width=24
        )
        search_entry.pack(side="left")

        tk.Label(
            toolbar,
            text="From (YYYY-MM-DD)",
            bg=BG,
            fg=TEXT
        ).pack(side="left", padx=(14, 6))

        from_var = tk.StringVar()

        ttk.Entry(
            toolbar,
            textvariable=from_var,
            width=12
        ).pack(side="left")

        tk.Label(
            toolbar,
            text="To",
            bg=BG,
            fg=TEXT
        ).pack(side="left", padx=(8, 5))

        to_var = tk.StringVar()

        ttk.Entry(
            toolbar,
            textvariable=to_var,
            width=12
        ).pack(side="left")

        # Add expense form
        form = tk.Frame(
            page,
            bg=WHITE,
            padx=14,
            pady=12,
            highlightbackground="#E1E7F0",
            highlightthickness=1
        )
        form.pack(fill="x", pady=(0, 12))

        fields = tk.Frame(form, bg=WHITE)
        fields.pack(fill="x")

        # NEW: Separate category dropdown for adding expenses
        add_category_var = tk.StringVar(value="")

        category_frame = tk.Frame(fields, bg=WHITE)
        category_frame.pack(side="left", padx=(0, 12))

        tk.Label(
            category_frame,
            text="Category",
            bg=WHITE,
            fg=MUTED,
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", pady=(0, 5))

        add_category_box = ttk.Combobox(
            category_frame,
            textvariable=add_category_var,
            values=list(CATEGORIES.keys()),
            state="readonly",
            width=17
        )
        add_category_box.pack(ipady=5)

        def make_field(label, width=17):
            wrap = tk.Frame(fields, bg=WHITE)
            wrap.pack(side="left", padx=(0, 12))

            tk.Label(
                wrap,
                text=label,
                bg=WHITE,
                fg=MUTED,
                font=("Segoe UI", 9, "bold")
            ).pack(anchor="w", pady=(0, 5))

            ent = ttk.Entry(wrap, width=width)
            ent.pack(ipady=5)
            return ent

        item_entry = make_field("Item name")
        qty_entry = make_field("Quantity")
        amount_entry = make_field("Total amount (₹)")
        date_entry = make_field("Expense date")

        date_entry.insert(0, date.today().isoformat())

        form_buttons = tk.Frame(form, bg=WHITE)
        form_buttons.pack(anchor="w", pady=(12, 0))

        # Expense table
        table_frame = tk.Frame(
            page,
            bg=WHITE,
            highlightbackground="#E1E7F0",
            highlightthickness=1
        )
        table_frame.pack(fill="both", expand=True)

        columns = (
            "id",
            "category",
            "item_name",
            "quantity",
            "unit_amount",
            "expense_date"
        )

        tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        headings = {
            "id": "ID",
            "category": "Category",
            "item_name": "Item",
            "quantity": "Quantity",
            "unit_amount": "Amount (₹)",
            "expense_date": "Date"
        }

        widths = {
            "id": 55,
            "category": 130,
            "item_name": 260,
            "quantity": 100,
            "unit_amount": 140,
            "expense_date": 130
        }

        for col in columns:
            tree.heading(col, text=headings[col])
            tree.column(col, width=widths[col], anchor="w")

        yscroll = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=tree.yview
        )

        xscroll = ttk.Scrollbar(
            table_frame,
            orient="horizontal",
            command=tree.xview
        )

        tree.configure(
            yscrollcommand=yscroll.set,
            xscrollcommand=xscroll.set
        )

        tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")

        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        def chosen_tables():
            name = selected_category.get()

            if name == "All categories":
                return list(CATEGORIES.items())

            return [(name, CATEGORIES[name])]

        # Load expense records
        def load_rows():

            nonlocal current_rows

            for node in tree.get_children():
                tree.delete(node)

            current_rows = []

            start = from_var.get().strip()
            end = to_var.get().strip()

            for value in (start, end):
                if value:
                    try:
                        datetime.strptime(value, "%Y-%m-%d")
                    except ValueError:
                        messagebox.showwarning(
                            "Invalid date",
                            "Use YYYY-MM-DD for date filters."
                        )
                        return

            conn = connect_to_database()
            cur = conn.cursor()

            try:
                for label, table in chosen_tables():

                    sql = (
                        f"SELECT id,item_name,quantity,"
                        f"unit_amount,expense_date "
                        f"FROM {table} WHERE 1=1"
                    )

                    params = []

                    if search_var.get().strip():
                        sql += " AND item_name LIKE %s"
                        params.append(
                            "%" + search_var.get().strip() + "%"
                        )

                    if start:
                        sql += " AND expense_date >= %s"
                        params.append(start)

                    if end:
                        sql += " AND expense_date <= %s"
                        params.append(end)

                    sql += " ORDER BY expense_date DESC, id DESC"

                    cur.execute(sql, tuple(params))

                    for row in cur.fetchall():
                        current_rows.append((label, table, row))

                        tree.insert(
                            "",
                            "end",
                            values=(
                                row[0],
                                label,
                                row[1],
                                row[2],
                                row[3],
                                row[4]
                            )
                        )

            except mysql.connector.Error as err:
                messagebox.showerror("Database error", str(err))

            finally:
                cur.close()
                conn.close()

        # Clear input fields
        def clear_form():

            selected_record_id.set(0)
            add_category_var.set("")

            for entry in (
                item_entry,
                qty_entry,
                amount_entry
            ):
                entry.delete(0, tk.END)

            date_entry.delete(0, tk.END)
            date_entry.insert(0, date.today().isoformat())

            tree.selection_remove(tree.selection())

        # Validate expense details
        def validate_form():

            item = item_entry.get().strip()
            qty = qty_entry.get().strip()
            amount = amount_entry.get().strip()
            exp_date = date_entry.get().strip()

            if not item:
                messagebox.showwarning(
                    "Missing item",
                    "Enter an item name."
                )
                return None

            try:
                quantity = float(qty)
                total_amount = float(amount)

                if quantity <= 0 or total_amount < 0:
                    raise ValueError

                datetime.strptime(exp_date, "%Y-%m-%d")

            except ValueError:
                messagebox.showwarning(
                    "Invalid details",
                    "Enter a positive quantity, a valid amount "
                    "and date (YYYY-MM-DD)."
                )
                return None

            return item, quantity, total_amount, exp_date

        # Add expense
        def add_record():

            details = validate_form()

            if not details:
                return

            # Use the NEW category dropdown, not the filter dropdown
            category = add_category_var.get()

            if not category:
                messagebox.showwarning(
                    "Choose category",
                    "Select a category before adding an expense."
                )
                return

            conn = None
            cur = None

            try:
                conn = connect_to_database()
                cur = conn.cursor()

                table = CATEGORIES[category]

                cur.execute(
                    f"INSERT INTO {table} "
                    "(item_name,quantity,unit_amount,expense_date) "
                    "VALUES (%s,%s,%s,%s)",
                    details
                )

                conn.commit()

                # Show records from the category just added
                selected_category.set(category)
                load_rows()
                clear_form()

                messagebox.showinfo(
                    "Saved",
                    "Expense added successfully."
                )

            except mysql.connector.Error as err:
                if conn:
                    conn.rollback()
                messagebox.showerror("Database error", str(err))

            finally:
                if cur:
                    cur.close()
                if conn:
                    conn.close()

        # Update expense
        def update_record():

            details = validate_form()

            if not details:
                return

            selection = tree.selection()

            if not selection:
                messagebox.showwarning(
                    "Select record",
                    "Select an expense record first."
                )
                return

            values = tree.item(selection[0], "values")
            table = CATEGORIES[values[1]]

            conn = None
            cur = None

            try:
                conn = connect_to_database()
                cur = conn.cursor()

                cur.execute(
                    f"UPDATE {table} SET "
                    "item_name=%s,quantity=%s,"
                    "unit_amount=%s,expense_date=%s "
                    "WHERE id=%s",
                    details + (values[0],)
                )

                conn.commit()
                load_rows()
                clear_form()

                messagebox.showinfo(
                    "Updated",
                    "Expense updated successfully."
                )

            except mysql.connector.Error as err:
                if conn:
                    conn.rollback()
                messagebox.showerror("Database error", str(err))

            finally:
                if cur:
                    cur.close()
                if conn:
                    conn.close()

        # Delete expense
        def delete_record():

            selection = tree.selection()

            if not selection:
                messagebox.showwarning(
                    "Select record",
                    "Select an expense record first."
                )
                return

            values = tree.item(selection[0], "values")

            if not messagebox.askyesno(
                "Confirm delete",
                f"Delete '{values[2]}'?"
            ):
                return

            conn = None
            cur = None

            try:
                conn = connect_to_database()
                cur = conn.cursor()

                cur.execute(
                    f"DELETE FROM {CATEGORIES[values[1]]} "
                    "WHERE id=%s",
                    (values[0],)
                )

                conn.commit()
                load_rows()
                clear_form()

            except mysql.connector.Error as err:
                if conn:
                    conn.rollback()
                messagebox.showerror("Database error", str(err))

            finally:
                if cur:
                    cur.close()
                if conn:
                    conn.close()

        # Select table row
        def select_row(event=None):

            selection = tree.selection()

            if not selection:
                return

            values = tree.item(selection[0], "values")

            # Fill the category dropdown also
            add_category_var.set(values[1])

            item_entry.delete(0, tk.END)
            item_entry.insert(0, values[2])

            qty_entry.delete(0, tk.END)
            qty_entry.insert(0, values[3])

            amount_entry.delete(0, tk.END)
            amount_entry.insert(0, values[4])

            date_entry.delete(0, tk.END)
            date_entry.insert(0, values[5])

        # Export records to CSV
        def export_csv():

            if not current_rows:
                messagebox.showinfo(
                    "No records",
                    "There are no records to export."
                )
                return

            path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                initialfile="expenses.csv"
            )

            if not path:
                return

            with open(
                path,
                "w",
                newline="",
                encoding="utf-8-sig"
            ) as file:

                writer = csv.writer(file)

                writer.writerow([
                    "ID",
                    "Category",
                    "Item",
                    "Quantity",
                    "Amount",
                    "Date"
                ])

                for label, table, row in current_rows:
                    writer.writerow([
                        row[0],
                        label,
                        row[1],
                        row[2],
                        row[3],
                        row[4]
                    ])

            messagebox.showinfo(
                "Export complete",
                "Expense records exported to CSV."
            )

        # Buttons
        def button(parent, text, command, color=BLUE):

            tk.Button(
                parent,
                text=text,
                command=command,
                bg=color,
                fg="white",
                activebackground=color,
                relief="flat",
                padx=13,
                pady=7,
                cursor="hand2",
                font=("Segoe UI", 9, "bold")
            ).pack(side="left", padx=(0, 8))

        button(form_buttons, "Add expense", add_record)
        button(form_buttons, "Update selected", update_record, "#16845B")
        button(form_buttons, "Delete selected", delete_record, "#D64545")
        button(form_buttons, "Clear", clear_form, "#64748B")

        button(toolbar, "Apply filters", load_rows)
        button(toolbar, "Export CSV", export_csv, "#16845B")

        category_box.bind(
            "<<ComboboxSelected>>",
            lambda e: load_rows()
        )

        tree.bind(
            "<<TreeviewSelect>>",
            select_row
        )

        load_rows()

    # Reports and charts
    def show_reports():

        set_title(
            "Reports & insights",
            "Compare category spending for a selected month."
        )

        clear_page()

        top = tk.Frame(page, bg=WHITE, padx=18, pady=16)
        top.pack(fill="x")

        tk.Label(
            top,
            text="Report month (YYYY-MM)",
            bg=WHITE,
            fg=TEXT,
            font=("Segoe UI", 10, "bold")
        ).pack(side="left")

        month_var = tk.StringVar(
            value=date.today().strftime("%Y-%m")
        )

        ttk.Entry(
            top,
            textvariable=month_var,
            width=12
        ).pack(side="left", padx=10)

        result_frame = tk.Frame(
            page,
            bg=WHITE,
            padx=18,
            pady=16
        )

        result_frame.pack(
            fill="both",
            expand=True,
            pady=14
        )

        def generate():

            month = month_var.get().strip()

            try:
                datetime.strptime(month, "%Y-%m")

            except ValueError:
                messagebox.showwarning(
                    "Invalid month",
                    "Enter month in YYYY-MM format."
                )
                return

            for child in result_frame.winfo_children():
                child.destroy()

            try:
                totals = all_totals(month)

            except mysql.connector.Error as err:
                messagebox.showerror(
                    "Report error",
                    f"Could not generate the report.\n\n{err}"
                )
                return

            grand_total = sum(totals.values())

            tk.Label(
                result_frame,
                text=f"Total for {month}: {money(grand_total)}",
                bg=WHITE,
                fg=NAVY,
                font=("Segoe UI", 16, "bold")
            ).pack(anchor="w")

            for name, amount in totals.items():
                tk.Label(
                    result_frame,
                    text=f"{name}: {money(amount)}",
                    bg=WHITE,
                    fg=TEXT,
                    font=("Segoe UI", 10)
                ).pack(anchor="w", pady=3)

            if grand_total == 0:
                tk.Label(
                    result_frame,
                    text="No expenses found for this month.",
                    bg=WHITE,
                    fg=MUTED,
                    font=("Segoe UI", 11)
                ).pack(anchor="w", pady=12)
                return

            fig, ax = plt.subplots(figsize=(7, 4), dpi=95)

            ax.bar(
                list(totals.keys()),
                list(totals.values())
            )

            ax.set_ylabel("Amount (₹)")
            ax.set_title(f"Expense breakdown - {month}")
            ax.spines[["top", "right"]].set_visible(False)

            fig.tight_layout()

            canvas = FigureCanvasTkAgg(
                fig,
                master=result_frame
            )

            canvas.draw()
            canvas.get_tk_widget().pack(
                fill="both",
                expand=True,
                pady=10
            )

            plt.close(fig)

        tk.Button(
            top,
            text="Generate report",
            command=generate,
            bg=BLUE,
            fg="white",
            relief="flat",
            padx=14,
            pady=7
        ).pack(side="left")

        generate()

    # Sidebar navigation
    nav_button("▦   Dashboard", show_dashboard)
    nav_button("＋   Manage expenses", show_expenses)
    nav_button("▤   Reports & charts", show_reports)

    tk.Frame(
        sidebar,
        bg="#E8EEF8",
        height=1
    ).pack(fill="x", padx=16, pady=14)

    tk.Button(
        sidebar,
        text="↪   Log out",
        command=close_app,
        anchor="w",
        bg=WHITE,
        fg="#C0392B",
        relief="flat",
        bd=0,
        font=("Segoe UI", 10, "bold"),
        padx=22,
        pady=14,
        cursor="hand2"
    ).pack(
        side="bottom",
        fill="x",
        padx=9,
        pady=12
    )

    show_dashboard()
    app.mainloop()


if __name__ == "__main__":
    open_main_form()
