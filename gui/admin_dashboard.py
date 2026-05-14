# gui/admin_dashboard.py

import tkinter as tk
from tkinter import ttk, messagebox
from gui.components import (
    SidebarButton, StatCard, PageHeader,
    FormField, ActionButton, make_table,
    BG_COLOR, SIDEBAR_COLOR, CARD_COLOR,
    ACCENT_COLOR, TEXT_COLOR, SUBTEXT_COLOR,
    SUCCESS_COLOR, WARNING_COLOR, INPUT_BG
)
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import calendar


class AdminDashboard:
    """
    The main Admin Dashboard window.

    OOP Concept - ENCAPSULATION:
    All admin UI logic lives here. The sidebar, content area,
    and all section methods are neatly contained in one class.
    """

    def __init__(self, root, user):
        self.root = root
        self.user = user  # Admin model instance

        self.root.title(user.get_dashboard_title())
        self.root.geometry("1200x720")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(True, True)
        self.center_window()

        self.active_btn = None  # Tracks which sidebar button is active
        self.build_layout()
        self.show_overview()   # Default section on load

    def center_window(self):
        w, h = 1200, 720
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    # ── Layout ────────────────────────────────────────────────────

    def build_layout(self):
        """Builds the two-column layout: sidebar + content area."""

        # Left sidebar
        self.sidebar = tk.Frame(
            self.root, bg=SIDEBAR_COLOR, width=220
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Right content area
        self.content = tk.Frame(self.root, bg=BG_COLOR)
        self.content.pack(side="right", fill="both", expand=True)

        self.build_sidebar()

    def build_sidebar(self):
        """Builds the sidebar logo and navigation buttons."""

        # Logo
        logo_frame = tk.Frame(self.sidebar, bg=ACCENT_COLOR, pady=18)
        logo_frame.pack(fill="x")

        tk.Label(
            logo_frame, text=" SmartFit",
            font=("Arial", 16, "bold"),
            bg=ACCENT_COLOR, fg="white"
        ).pack()

        tk.Label(
            logo_frame, text="Admin Panel",
            font=("Arial", 9),
            bg=ACCENT_COLOR, fg="#ffd0d8"
        ).pack()

        # Admin name
        tk.Label(
            self.sidebar,
            text=f"👤 {self.user.full_name}",
            font=("Arial", 9),
            bg=SIDEBAR_COLOR, fg=SUBTEXT_COLOR,
            wraplength=200
        ).pack(pady=(12, 4))

        tk.Frame(self.sidebar, bg=CARD_COLOR, height=1).pack(
            fill="x", padx=15, pady=6
        )

        # Navigation buttons
        nav_items = [
            ("Overview",    "🏠", self.show_overview),
            ("Members",     "👥", self.show_members),
            ("Trainers",    "🏋️", self.show_trainers),
            ("Plans",       "📋", self.show_plans),
            ("Payments",    "💳", self.show_payments),
            ("Attendance",  "", self.show_attendance),
            ("Workouts",    "", self.show_workouts),
        ]

        self.nav_buttons = {}
        for name, icon, cmd in nav_items:
            btn = SidebarButton(self.sidebar, name, icon, cmd)
            btn.pack(fill="x", padx=8, pady=2)
            self.nav_buttons[name] = btn

        # Logout at the bottom
        tk.Frame(self.sidebar, bg=CARD_COLOR, height=1).pack(
            fill="x", padx=15, pady=6, side="bottom"
        )
        ActionButton(
            self.sidebar, "Logout", self.logout,
            style="danger", icon=""
        ).pack(fill="x", padx=8, pady=8, side="bottom")

    def set_active_nav(self, name):
        """Highlights the active sidebar button."""
        for btn_name, btn in self.nav_buttons.items():
            if btn_name == name:
                btn.set_active()
            else:
                btn.set_inactive()

    def clear_content(self):
        """Clears the content area before loading a new section."""
        for widget in self.content.winfo_children():
            widget.destroy()

    # ── Overview ─────────────────────────────────────────────────

    def show_overview(self):
        self.clear_content()
        self.set_active_nav("Overview")

        frame = tk.Frame(self.content, bg=BG_COLOR, padx=24, pady=20)
        frame.pack(fill="both", expand=True)

        PageHeader(
            frame,
            "Dashboard Overview",
            f"Welcome back, {self.user.full_name}  •  {date.today().strftime('%B %d, %Y')}"
        ).pack(fill="x", pady=(0, 20))

        # Stat cards
        stats = self.user.get_dashboard_stats()

        cards_frame = tk.Frame(frame, bg=BG_COLOR)
        cards_frame.pack(fill="x", pady=(0, 24))

        card_data = [
            ("Active Members",   stats["active_members"],   "👥", ACCENT_COLOR),
            ("Active Trainers",  stats["active_trainers"],  "🏋️", SUCCESS_COLOR),
            ("Monthly Revenue",  f"KES {stats['monthly_revenue']:,.0f}", "💳", WARNING_COLOR),
            ("Today Attendance", stats["today_attendance"], "📅", "#9b59b6"),
        ]

        for i, (title, value, icon, color) in enumerate(card_data):
            card = StatCard(cards_frame, title, value, icon, color)
            card.grid(row=0, column=i, padx=8, pady=4, sticky="ew")
            cards_frame.columnconfigure(i, weight=1)

        # Recent members table
        tk.Label(
            frame, text="Recent Members",
            font=("Arial", 13, "bold"),
            bg=BG_COLOR, fg=TEXT_COLOR
        ).pack(anchor="w", pady=(8, 6))

        cols = ["Name", "Username", "Plan", "Status", "Expires"]
        tree, tframe = make_table(frame, cols, heights=8)
        tframe.pack(fill="both", expand=True)

        members = self.user.get_all_members()
        for m in members[:10]:
            tree.insert("", "end", values=(
                m["full_name"], m["username"],
                m["membership_plan"], m["status"],
                m["membership_end"] or "N/A"
            ))

    # ── Members ──────────────────────────────────────────────────

    def show_members(self):
        self.clear_content()
        self.set_active_nav("Members")

        frame = tk.Frame(self.content, bg=BG_COLOR, padx=24, pady=20)
        frame.pack(fill="both", expand=True)

        PageHeader(frame, "Member Management", "Add, edit, and manage gym members").pack(
            fill="x", pady=(0, 16)
        )

        # Top bar — search + add button
        top = tk.Frame(frame, bg=BG_COLOR)
        top.pack(fill="x", pady=(0, 10))

        self.member_search_var = tk.StringVar()
        search_entry = tk.Entry(
            top, textvariable=self.member_search_var,
            font=("Arial", 11), bg=CARD_COLOR, fg=TEXT_COLOR,
            insertbackground=TEXT_COLOR, relief="flat", bd=0
        )
        search_entry.pack(side="left", ipady=7, ipadx=10, padx=(0, 8))
        search_entry.insert(0, "🔍  Search members...")
        search_entry.bind("<FocusIn>",  lambda e: search_entry.delete(0, "end")
                          if search_entry.get().startswith("🔍") else None)
        search_entry.bind("<KeyRelease>", lambda e: self.search_members())

        ActionButton(top, "Add Member", self.open_add_member_form,
                     icon="➕").pack(side="left", padx=4)
        ActionButton(top, "Delete Selected", self.delete_member,
                     style="danger", icon="🗑️").pack(side="left", padx=4)
        ActionButton(top, "Record Check-In", self.record_checkin,
                     style="success", icon="✅").pack(side="left", padx=4)

        # Members table
        cols = ["ID", "Full Name", "Username", "Email",
                "Phone", "Plan", "Status", "Expires"]
        self.members_tree, tframe = make_table(frame, cols, heights=16)
        tframe.pack(fill="both", expand=True)

        # Set column widths
        widths = [40, 160, 110, 180, 110, 90, 80, 100]
        for col, w in zip(cols, widths):
            self.members_tree.column(col, width=w, anchor="w")

        self.load_members_table()

    def load_members_table(self, keyword=""):
        """Loads or refreshes the members table."""
        for row in self.members_tree.get_children():
            self.members_tree.delete(row)

        members = (self.user.search_members(keyword)
                   if keyword else self.user.get_all_members())

        for m in members:
            self.members_tree.insert("", "end", values=(
                m["id"], m["full_name"], m["username"],
                m["email"] or "", m["phone"] or "",
                m["membership_plan"], m["status"],
                m["membership_end"] or "N/A"
            ))

    def search_members(self):
        kw = self.member_search_var.get().strip()
        if kw and not kw.startswith("🔍"):
            self.load_members_table(kw)
        else:
            self.load_members_table()

    def open_add_member_form(self):
        """Opens a popup form to add a new member."""
        win = tk.Toplevel(self.root)
        win.title("Add New Member")
        win.geometry("460x620")
        win.configure(bg=CARD_COLOR)
        win.resizable(False, False)
        self._center_popup(win, 460, 620)

        tk.Label(
            win, text="➕  Add New Member",
            font=("Arial", 14, "bold"),
            bg=CARD_COLOR, fg=TEXT_COLOR
        ).pack(pady=(20, 4), padx=24, anchor="w")

        tk.Frame(win, bg=ACCENT_COLOR, height=2).pack(
            fill="x", padx=24, pady=(0, 16)
        )

        # Form fields
        fields = {}
        field_defs = [
            ("Full Name",  "full_name",  ""),
            ("Username",   "username",   ""),
            ("Password",   "password",   "●"),
            ("Email",      "email",      ""),
            ("Phone",      "phone",      ""),
        ]

        for label, key, show in field_defs:
            f = FormField(win, label, show=show)
            f.pack(fill="x", padx=24)
            fields[key] = f

        # Plan dropdown
        tk.Label(
            win, text="Membership Plan",
            font=("Arial", 9), bg=CARD_COLOR, fg=SUBTEXT_COLOR
        ).pack(anchor="w", padx=24)

        plans = self.user.get_all_plans()
        plan_names = [p["plan_name"] for p in plans]
        plan_var = tk.StringVar(value=plan_names[0] if plan_names else "Basic")

        plan_menu = ttk.Combobox(
            win, textvariable=plan_var,
            values=plan_names, state="readonly",
            font=("Arial", 11)
        )
        plan_menu.pack(fill="x", padx=24, ipady=6, pady=(2, 10))

        # Start date
        tk.Label(
            win, text="Membership Start (YYYY-MM-DD)",
            font=("Arial", 9), bg=CARD_COLOR, fg=SUBTEXT_COLOR
        ).pack(anchor="w", padx=24)

        start_var = tk.StringVar(value=str(date.today()))
        tk.Entry(
            win, textvariable=start_var,
            font=("Arial", 11), bg=INPUT_BG, fg=TEXT_COLOR,
            insertbackground=TEXT_COLOR, relief="flat"
        ).pack(fill="x", padx=24, ipady=7, pady=(2, 16))

        def submit():
            # Gather values
            data = {k: f.get() for k, f in fields.items()}
            plan  = plan_var.get()
            start = start_var.get().strip()

            # Basic validation
            if not all([data["full_name"], data["username"], data["password"]]):
                messagebox.showerror("Error", "Name, username and password are required.", parent=win)
                return

            # Calculate end date based on plan duration
            selected_plan = next((p for p in plans if p["plan_name"] == plan), None)
            if selected_plan:
                try:
                    start_dt = datetime.strptime(start, "%Y-%m-%d").date()
                    end_dt   = start_dt + relativedelta(
                        months=selected_plan["duration_months"]
                    )
                    end = str(end_dt)
                except ValueError:
                    messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD", parent=win)
                    return
            else:
                end = start

            success, msg = self.user.add_member(
                data["username"], data["password"], data["full_name"],
                data["email"], data["phone"], plan, start, end
            )

            if success:
                messagebox.showinfo("Success", msg, parent=win)
                win.destroy()
                self.load_members_table()
            else:
                messagebox.showerror("Error", msg, parent=win)

        ActionButton(win, "Save Member", submit, icon="").pack(
            padx=24, pady=8, fill="x"
        )
        ActionButton(win, "Cancel", win.destroy, style="neutral").pack(
            padx=24, fill="x"
        )

    def delete_member(self):
        selected = self.members_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a member to delete.")
            return

        values = self.members_tree.item(selected[0])["values"]
        user_id   = values[0]
        full_name = values[1]

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete '{full_name}'?\nThis cannot be undone."
        )
        if confirm:
            self.user.delete_member(user_id)
            self.load_members_table()
            messagebox.showinfo("Deleted", f"'{full_name}' has been removed.")

    def record_checkin(self):
        """Records a check-in for the selected member."""
        selected = self.members_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a member.")
            return

        values   = self.members_tree.item(selected[0])["values"]
        user_id  = values[0]
        name     = values[1]

        conn = self.user._db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM members WHERE user_id=?", (user_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            member_id = row["id"]
            conn = self.user._db.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO attendance (member_id) VALUES (?)", (member_id,)
            )
            conn.commit()
            conn.close()
            messagebox.showinfo("Check-In", f"✅ {name} checked in successfully!")
        else:
            messagebox.showerror("Error", "Member record not found.")

    # ── Trainers ─────────────────────────────────────────────────

    def show_trainers(self):
        self.clear_content()
        self.set_active_nav("Trainers")

        frame = tk.Frame(self.content, bg=BG_COLOR, padx=24, pady=20)
        frame.pack(fill="both", expand=True)

        PageHeader(frame, "Trainer Management", "Manage your gym trainers").pack(
            fill="x", pady=(0, 16)
        )

        top = tk.Frame(frame, bg=BG_COLOR)
        top.pack(fill="x", pady=(0, 10))

        ActionButton(top, "Add Trainer", self.open_add_trainer_form,
                     icon="➕").pack(side="left", padx=4)
        ActionButton(top, "Delete Selected", self.delete_trainer,
                     style="danger", icon="🗑️").pack(side="left", padx=4)

        cols = ["ID", "Full Name", "Email", "Phone", "Specialty",
                "Hire Date", "Status"]
        self.trainers_tree, tframe = make_table(frame, cols, heights=16)
        tframe.pack(fill="both", expand=True)

        widths = [40, 160, 180, 120, 140, 110, 80]
        for col, w in zip(cols, widths):
            self.trainers_tree.column(col, width=w)

        self.load_trainers_table()

    def load_trainers_table(self):
        for row in self.trainers_tree.get_children():
            self.trainers_tree.delete(row)
        for t in self.user.get_all_trainers():
            self.trainers_tree.insert("", "end", values=(
                t["id"], t["full_name"], t["email"] or "",
                t["phone"] or "", t["specialty"] or "",
                t["hire_date"] or "", t["status"]
            ))

    def open_add_trainer_form(self):
        win = tk.Toplevel(self.root)
        win.title("Add Trainer")
        win.geometry("420x420")
        win.configure(bg=CARD_COLOR)
        self._center_popup(win, 420, 420)

        tk.Label(
            win, text="➕  Add New Trainer",
            font=("Arial", 14, "bold"),
            bg=CARD_COLOR, fg=TEXT_COLOR
        ).pack(pady=(20, 4), padx=24, anchor="w")
        tk.Frame(win, bg=ACCENT_COLOR, height=2).pack(
            fill="x", padx=24, pady=(0, 16)
        )

        fields = {}
        for label, key in [("Full Name","full_name"),("Email","email"),
                            ("Phone","phone"),("Specialty","specialty")]:
            f = FormField(win, label)
            f.pack(fill="x", padx=24)
            fields[key] = f

        def submit():
            d = {k: f.get() for k, f in fields.items()}
            if not d["full_name"]:
                messagebox.showerror("Error", "Full name is required.", parent=win)
                return
            self.user.add_trainer(
                d["full_name"], d["email"], d["phone"], d["specialty"]
            )
            messagebox.showinfo("Success", "Trainer added!", parent=win)
            win.destroy()
            self.load_trainers_table()

        ActionButton(win, "Save Trainer", submit, icon="").pack(
            padx=24, pady=10, fill="x"
        )
        ActionButton(win, "Cancel", win.destroy, style="neutral").pack(
            padx=24, fill="x"
        )

    def delete_trainer(self):
        selected = self.trainers_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a trainer.")
            return
        values    = self.trainers_tree.item(selected[0])["values"]
        trainer_id = values[0]
        name       = values[1]
        if messagebox.askyesno("Confirm", f"Delete trainer '{name}'?"):
            conn = self.user._db.get_connection()
            conn.cursor().execute(
                "DELETE FROM trainers WHERE id=?", (trainer_id,)
            )
            conn.commit()
            conn.close()
            self.load_trainers_table()

    # ── Plans ────────────────────────────────────────────────────

    def show_plans(self):
        self.clear_content()
        self.set_active_nav("Plans")

        frame = tk.Frame(self.content, bg=BG_COLOR, padx=24, pady=20)
        frame.pack(fill="both", expand=True)

        PageHeader(frame, "Membership Plans",
                   "Create and manage subscription plans").pack(
            fill="x", pady=(0, 16)
        )

        top = tk.Frame(frame, bg=BG_COLOR)
        top.pack(fill="x", pady=(0, 10))
        ActionButton(top, "Add Plan", self.open_add_plan_form,
                     icon="➕").pack(side="left", padx=4)
        ActionButton(top, "Delete Selected", self.delete_plan,
                     style="danger", icon="🗑️").pack(side="left", padx=4)

        cols = ["ID", "Plan Name", "Duration (Months)", "Price (KES)", "Description"]
        self.plans_tree, tframe = make_table(frame, cols, heights=14)
        tframe.pack(fill="both", expand=True)
        self.plans_tree.column("Description", width=300)
        self.load_plans_table()

    def load_plans_table(self):
        for row in self.plans_tree.get_children():
            self.plans_tree.delete(row)
        for p in self.user.get_all_plans():
            self.plans_tree.insert("", "end", values=(
                p["id"], p["plan_name"],
                p["duration_months"],
                f"{p['price']:,.0f}",
                p["description"] or ""
            ))

    def open_add_plan_form(self):
        win = tk.Toplevel(self.root)
        win.title("Add Plan")
        win.geometry("420x380")
        win.configure(bg=CARD_COLOR)
        self._center_popup(win, 420, 380)

        tk.Label(
            win, text="➕  Add Membership Plan",
            font=("Arial", 14, "bold"),
            bg=CARD_COLOR, fg=TEXT_COLOR
        ).pack(pady=(20, 4), padx=24, anchor="w")
        tk.Frame(win, bg=ACCENT_COLOR, height=2).pack(
            fill="x", padx=24, pady=(0, 16)
        )

        f_name = FormField(win, "Plan Name")
        f_name.pack(fill="x", padx=24)
        f_dur  = FormField(win, "Duration (months)")
        f_dur.pack(fill="x", padx=24)
        f_price = FormField(win, "Price (KES)")
        f_price.pack(fill="x", padx=24)
        f_desc  = FormField(win, "Description")
        f_desc.pack(fill="x", padx=24)

        def submit():
            name  = f_name.get()
            dur   = f_dur.get()
            price = f_price.get()
            desc  = f_desc.get()
            if not name or not dur or not price:
                messagebox.showerror("Error", "Name, duration and price required.",
                                     parent=win)
                return
            try:
                conn = self.user._db.get_connection()
                conn.cursor().execute("""
                    INSERT INTO membership_plans
                    (plan_name, duration_months, price, description)
                    VALUES (?, ?, ?, ?)
                """, (name, int(dur), float(price), desc))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Plan added!", parent=win)
                win.destroy()
                self.load_plans_table()
            except Exception as ex:
                messagebox.showerror("Error", str(ex), parent=win)

        ActionButton(win, "Save Plan", submit, icon="").pack(
            padx=24, pady=10, fill="x"
        )
        ActionButton(win, "Cancel", win.destroy, style="neutral").pack(
            padx=24, fill="x"
        )

    def delete_plan(self):
        selected = self.plans_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a plan to delete.")
            return
        values  = self.plans_tree.item(selected[0])["values"]
        plan_id = values[0]
        name    = values[1]
        if messagebox.askyesno("Confirm", f"Delete plan '{name}'?"):
            conn = self.user._db.get_connection()
            conn.cursor().execute(
                "DELETE FROM membership_plans WHERE id=?", (plan_id,)
            )
            conn.commit()
            conn.close()
            self.load_plans_table()

    # ── Payments ─────────────────────────────────────────────────

    def show_payments(self):
        self.clear_content()
        self.set_active_nav("Payments")

        frame = tk.Frame(self.content, bg=BG_COLOR, padx=24, pady=20)
        frame.pack(fill="both", expand=True)

        PageHeader(frame, "Payment Records",
                   "Track all member payments").pack(fill="x", pady=(0, 16))

        top = tk.Frame(frame, bg=BG_COLOR)
        top.pack(fill="x", pady=(0, 10))
        ActionButton(top, "Record Payment",
                     self.open_add_payment_form, icon="➕").pack(
            side="left", padx=4
        )

        cols = ["ID", "Member Name", "Amount (KES)",
                "Plan", "Date", "Method", "Status"]
        self.payments_tree, tframe = make_table(frame, cols, heights=16)
        tframe.pack(fill="both", expand=True)
        self.load_payments_table()

    def load_payments_table(self):
        for row in self.payments_tree.get_children():
            self.payments_tree.delete(row)
        for p in self.user.get_all_payments():
            self.payments_tree.insert("", "end", values=(
                p["id"], p["full_name"],
                f"{p['amount']:,.0f}",
                p["plan_name"] or "",
                p["payment_date"],
                p["payment_method"],
                p["status"]
            ))

    def open_add_payment_form(self):
        win = tk.Toplevel(self.root)
        win.title("Record Payment")
        win.geometry("420x420")
        win.configure(bg=CARD_COLOR)
        self._center_popup(win, 420, 420)

        tk.Label(
            win, text="💳  Record Payment",
            font=("Arial", 14, "bold"),
            bg=CARD_COLOR, fg=TEXT_COLOR
        ).pack(pady=(20, 4), padx=24, anchor="w")
        tk.Frame(win, bg=ACCENT_COLOR, height=2).pack(
            fill="x", padx=24, pady=(0, 16)
        )

        # Member dropdown
        tk.Label(win, text="Select Member", font=("Arial", 9),
                 bg=CARD_COLOR, fg=SUBTEXT_COLOR).pack(anchor="w", padx=24)

        members = self.user.get_all_members()
        member_map = {m["full_name"]: m["member_id"] for m in members}
        member_var = tk.StringVar()
        ttk.Combobox(
            win, textvariable=member_var,
            values=list(member_map.keys()),
            state="readonly", font=("Arial", 11)
        ).pack(fill="x", padx=24, ipady=6, pady=(2, 10))

        f_amount = FormField(win, "Amount (KES)")
        f_amount.pack(fill="x", padx=24)

        tk.Label(win, text="Plan", font=("Arial", 9),
                 bg=CARD_COLOR, fg=SUBTEXT_COLOR).pack(anchor="w", padx=24)
        plans    = self.user.get_all_plans()
        plan_var = tk.StringVar()
        ttk.Combobox(
            win, textvariable=plan_var,
            values=[p["plan_name"] for p in plans],
            state="readonly", font=("Arial", 11)
        ).pack(fill="x", padx=24, ipady=6, pady=(2, 10))

        tk.Label(win, text="Payment Method", font=("Arial", 9),
                 bg=CARD_COLOR, fg=SUBTEXT_COLOR).pack(anchor="w", padx=24)
        method_var = tk.StringVar(value="Cash")
        ttk.Combobox(
            win, textvariable=method_var,
            values=["Cash", "M-Pesa", "Card", "Bank Transfer"],
            state="readonly", font=("Arial", 11)
        ).pack(fill="x", padx=24, ipady=6, pady=(2, 16))

        def submit():
            name   = member_var.get()
            amount = f_amount.get()
            plan   = plan_var.get()
            method = method_var.get()

            if not name or not amount:
                messagebox.showerror("Error", "Member and amount are required.",
                                     parent=win)
                return
            member_id = member_map.get(name)
            self.user.add_payment(member_id, float(amount), plan, method)
            messagebox.showinfo("Success", "Payment recorded!", parent=win)
            win.destroy()
            self.load_payments_table()

        ActionButton(win, "Save Payment", submit, icon="").pack(
            padx=24, pady=8, fill="x"
        )
        ActionButton(win, "Cancel", win.destroy, style="neutral").pack(
            padx=24, fill="x"
        )

    # ── Attendance ───────────────────────────────────────────────

    def show_attendance(self):
        self.clear_content()
        self.set_active_nav("Attendance")

        frame = tk.Frame(self.content, bg=BG_COLOR, padx=24, pady=20)
        frame.pack(fill="both", expand=True)

        PageHeader(frame, "Attendance Records",
                   "View all member check-ins").pack(fill="x", pady=(0, 16))

        ActionButton(
            frame, "Refresh", self.show_attendance,
            style="neutral", icon=""
        ).pack(anchor="w", pady=(0, 10))

        cols = ["ID", "Member Name", "Check-In Time", "Check-Out Time"]
        self.attendance_tree, tframe = make_table(frame, cols, heights=18)
        tframe.pack(fill="both", expand=True)

        widths = [50, 200, 200, 200]
        for col, w in zip(cols, widths):
            self.attendance_tree.column(col, width=w)

        for rec in self.user.get_all_attendance():
            self.attendance_tree.insert("", "end", values=(
                rec["id"], rec["full_name"],
                rec["check_in"], rec["check_out"] or "Still In"
            ))

    # ── Workouts ─────────────────────────────────────────────────

    def show_workouts(self):
        self.clear_content()
        self.set_active_nav("Workouts")

        frame = tk.Frame(self.content, bg=BG_COLOR, padx=24, pady=20)
        frame.pack(fill="both", expand=True)

        PageHeader(frame, "Workout Plans",
                   "Assign workout plans to members").pack(
            fill="x", pady=(0, 16)
        )

        top = tk.Frame(frame, bg=BG_COLOR)
        top.pack(fill="x", pady=(0, 10))
        ActionButton(top, "Assign Workout Plan",
                     self.open_assign_workout_form, icon="➕").pack(
            side="left", padx=4
        )

        cols = ["ID", "Member", "Plan Name", "Exercises", "Assigned Date"]
        self.workouts_tree, tframe = make_table(frame, cols, heights=16)
        tframe.pack(fill="both", expand=True)
        self.workouts_tree.column("Exercises", width=300)
        self.load_workouts_table()

    def load_workouts_table(self):
        for row in self.workouts_tree.get_children():
            self.workouts_tree.delete(row)

        conn = self.user._db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT w.id, u.full_name, w.plan_name,
                   w.exercises, w.created_at
            FROM workout_plans w
            JOIN members m ON w.member_id = m.id
            JOIN users u   ON m.user_id   = u.id
            ORDER BY w.created_at DESC
        """)
        for row in cursor.fetchall():
            self.workouts_tree.insert("", "end", values=(
                row["id"], row["full_name"], row["plan_name"],
                row["exercises"] or "", row["created_at"]
            ))
        conn.close()

    def open_assign_workout_form(self):
        win = tk.Toplevel(self.root)
        win.title("Assign Workout Plan")
        win.geometry("460x480")
        win.configure(bg=CARD_COLOR)
        self._center_popup(win, 460, 480)

        tk.Label(
            win, text="  Assign Workout Plan",
            font=("Arial", 14, "bold"),
            bg=CARD_COLOR, fg=TEXT_COLOR
        ).pack(pady=(20, 4), padx=24, anchor="w")
        tk.Frame(win, bg=ACCENT_COLOR, height=2).pack(
            fill="x", padx=24, pady=(0, 16)
        )

        tk.Label(win, text="Select Member", font=("Arial", 9),
                 bg=CARD_COLOR, fg=SUBTEXT_COLOR).pack(anchor="w", padx=24)
        members   = self.user.get_all_members()
        member_map = {m["full_name"]: m["member_id"] for m in members}
        member_var = tk.StringVar()
        ttk.Combobox(
            win, textvariable=member_var,
            values=list(member_map.keys()),
            state="readonly", font=("Arial", 11)
        ).pack(fill="x", padx=24, ipady=6, pady=(2, 10))

        f_plan = FormField(win, "Plan Name (e.g. Weight Loss Program)")
        f_plan.pack(fill="x", padx=24)

        tk.Label(win, text="Exercises (describe the routine)",
                 font=("Arial", 9), bg=CARD_COLOR,
                 fg=SUBTEXT_COLOR).pack(anchor="w", padx=24)

        exercises_text = tk.Text(
            win, height=6, font=("Arial", 11),
            bg=INPUT_BG, fg=TEXT_COLOR,
            insertbackground=TEXT_COLOR, relief="flat"
        )
        exercises_text.pack(fill="x", padx=24, pady=(4, 16))

        def submit():
            name      = member_var.get()
            plan_name = f_plan.get()
            exercises = exercises_text.get("1.0", "end").strip()
            if not name or not plan_name:
                messagebox.showerror("Error", "Member and plan name required.",
                                     parent=win)
                return
            member_id = member_map.get(name)
            conn = self.user._db.get_connection()
            conn.cursor().execute("""
                INSERT INTO workout_plans
                (member_id, plan_name, exercises, assigned_by)
                VALUES (?, ?, ?, ?)
            """, (member_id, plan_name, exercises, self.user.user_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Workout plan assigned!", parent=win)
            win.destroy()
            self.load_workouts_table()

        ActionButton(win, "Assign Plan", submit, icon="").pack(
            padx=24, pady=4, fill="x"
        )
        ActionButton(win, "Cancel", win.destroy, style="neutral").pack(
            padx=24, fill="x"
        )

    # ── Helpers ───────────────────────────────────────────────────

    def _center_popup(self, win, w, h):
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        win.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.root.destroy()
            import main
            main.main()