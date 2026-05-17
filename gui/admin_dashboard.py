# =============================================================
# The Admin Dashboard — the main screen for admin users.
#
# Layout:
#   Left  — fixed sidebar with navigation buttons
#   Right — content area that swaps between sections
#
# Sections: Overview, Members, Trainers, Plans,
#           Payments, Attendance, Workouts, Analytics
#
# OOP Concept - ENCAPSULATION:
# All admin UI logic and data operations are contained here.
# The sidebar, section rendering, and popup forms are all
# private methods (prefixed with _) that the outside world
# does not need to know about.
# =============================================================

import tkinter as tk
from tkinter import ttk, messagebox
from gui.components import (
    SidebarButton, make_table, header, card,
    form_row, popup, popup_header, dropdown,
    btn, lbl,
    BG_COLOR, SIDEBAR_COLOR, CARD_COLOR, ACCENT_COLOR,
    TEXT_COLOR, SUBTEXT_COLOR, SUCCESS_COLOR,
    WARNING_COLOR, INPUT_BG
)
from datetime import date
from dateutil.relativedelta import relativedelta


class AdminDashboard:
    """
    The admin dashboard window.

    Receives an Admin model instance (self.user) which provides
    all database operations. The dashboard calls methods on the
    Admin model to read and write data, then displays results.

    OOP Concept - COMPOSITION:
    AdminDashboard does not do database work itself.
    It delegates that to the Admin model instance (self.user).
    """

    def __init__(self, root, user):
        """
        Initialises the dashboard window and builds the layout.

        Parameters:
            root — the Toplevel window opened after login
            user — an Admin model instance with db methods
        """
        self.root = root
        self.user = user

        self.root.title("SmartFit  -  Admin Dashboard")
        self.root.geometry("1200x720")
        self.root.configure(bg=BG_COLOR)

        # Centre window on screen
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        self.root.geometry(
            f"1200x720+{(sw - 1200) // 2}+{(sh - 720) // 2}")

        self._build_layout()
        self.show_overview()   # load Overview section on start

    # ── Layout builders ───────────────────────────────────────

    def _build_layout(self):
        """
        Creates the two-column layout:
          Left  — sidebar (fixed width, never resizes)
          Right — content area (fills remaining space)
        """
        self.sidebar = tk.Frame(
            self.root, bg=SIDEBAR_COLOR, width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)   # prevent shrinking

        self.content = tk.Frame(self.root, bg=BG_COLOR)
        self.content.pack(side="right", fill="both", expand=True)

        self._build_sidebar()

    def _build_sidebar(self):
        """
        Populates the sidebar with:
          - App logo / name
          - Logged-in admin name
          - Navigation buttons (one per section)
          - Logout button pinned to the bottom
        """
        # Logo area
        logo = tk.Frame(self.sidebar, bg=ACCENT_COLOR, pady=18)
        logo.pack(fill="x")
        tk.Label(
            logo, text="SMARTFIT",
            font=("Arial", 16, "bold"),
            bg=ACCENT_COLOR, fg="white"
        ).pack()
        tk.Label(
            logo, text="Admin Panel",
            font=("Arial", 9),
            bg=ACCENT_COLOR, fg="#ffd0d8"
        ).pack()

        # Admin name below logo
        lbl(self.sidebar, self.user.full_name, 9,
            color=SUBTEXT_COLOR, bg=SIDEBAR_COLOR,
            wraplength=200).pack(pady=(10, 4))

        tk.Frame(self.sidebar, bg=CARD_COLOR, height=1).pack(
            fill="x", padx=14, pady=6)

        # Navigation items — (label, method to call on click)
        nav = [
            ("Overview",   self.show_overview),
            ("Members",    self.show_members),
            ("Trainers",   self.show_trainers),
            ("Plans",      self.show_plans),
            ("Payments",   self.show_payments),
            ("Attendance", self.show_attendance),
            ("Workouts",   self.show_workouts),
            ("Analytics",  self.show_analytics),
        ]

        # Keep a reference to each button so we can
        # highlight the active one when sections change
        self.nav_btns = {}
        for name, cmd in nav:
            b = SidebarButton(self.sidebar, name, cmd)
            b.pack(fill="x", padx=8, pady=2)
            self.nav_btns[name] = b

        # Divider then logout button pinned to the bottom
        tk.Frame(self.sidebar, bg=CARD_COLOR, height=1).pack(
            fill="x", padx=14, pady=6, side="bottom")
        btn(
            self.sidebar, "Logout", self.logout, bg="#c0392b"
        ).pack(fill="x", padx=8, pady=8, side="bottom")

    # ── Navigation helpers ────────────────────────────────────

    def _set_nav(self, name):
        """
        Highlights the active sidebar button and resets all others.
        Called at the start of every show_* section method.
        """
        for k, b in self.nav_btns.items():
            b.set_active() if k == name else b.set_inactive()

    def _clear(self):
        """
        Removes all widgets from the content area.
        Called before rendering a new section so the old one
        is fully replaced.
        """
        for widget in self.content.winfo_children():
            widget.destroy()

    def _frame(self):
        """
        Creates and returns a padded content frame inside the
        content area. Every section starts by calling this.
        """
        f = tk.Frame(self.content, bg=BG_COLOR, padx=24, pady=20)
        f.pack(fill="both", expand=True)
        return f

    # ── Overview section ──────────────────────────────────────

    def show_overview(self):
        """
        Displays the dashboard home screen with:
          - Four stat cards (members, trainers, revenue, check-ins)
          - A table of the 10 most recent members
        Data is fetched live from the database on every visit.
        """
        self._clear()
        self._set_nav("Overview")
        f = self._frame()

        header(f, "Dashboard Overview",
               date.today().strftime("%B %d, %Y")).pack(
            fill="x", pady=(0, 18))

        # Fetch live stats from the Admin model
        stats = self.user.get_dashboard_stats()

        # Stat cards row
        row = tk.Frame(f, bg=BG_COLOR)
        row.pack(fill="x", pady=(0, 20))

        for i, (title, val, color) in enumerate([
            ("Active Members",
             stats["active_members"],   ACCENT_COLOR),
            ("Active Trainers",
             stats["active_trainers"],  SUCCESS_COLOR),
            ("Monthly Revenue",
             f"KES {stats['monthly_revenue']:,.0f}", WARNING_COLOR),
            ("Today Check-ins",
             stats["today_attendance"], "#9b59b6"),
        ]):
            c = card(row)
            c.grid(row=0, column=i, padx=6, sticky="ew")
            row.columnconfigure(i, weight=1)
            lbl(c, str(val), 20, bold=True,
                color=color, bg=CARD_COLOR).pack(anchor="w")
            lbl(c, title, 9,
                color=SUBTEXT_COLOR, bg=CARD_COLOR).pack(anchor="w")

        # Recent members preview table
        lbl(f, "Recent Members", 13, bold=True).pack(
            anchor="w", pady=(4, 6))
        tree, tf = make_table(
            f, ["Name", "Username", "Plan", "Status", "Expires"], 8)
        tf.pack(fill="both", expand=True)

        for m in self.user.get_all_members()[:10]:
            tree.insert("", "end", values=(
                m["full_name"], m["username"],
                m["membership_plan"], m["status"],
                m["membership_end"] or "N/A"))

    # ── Members section ───────────────────────────────────────

    def show_members(self):
        """
        Displays the member management screen with:
          - Live search bar (filters as you type)
          - Add / Edit / Delete / Check-In action buttons
          - Full members table with 8 columns
        """
        self._clear()
        self._set_nav("Members")
        f = self._frame()

        header(f, "Member Management",
               "Add, edit, search and manage members").pack(
            fill="x", pady=(0, 14))

        # Top action bar
        top = tk.Frame(f, bg=BG_COLOR)
        top.pack(fill="x", pady=(0, 10))

        # Search entry — filters table as user types
        self._sv = tk.StringVar()
        se = tk.Entry(
            top, textvariable=self._sv,
            font=("Arial", 11), bg=CARD_COLOR,
            fg=TEXT_COLOR, insertbackground=TEXT_COLOR,
            relief="flat"
        )
        se.pack(side="left", ipady=7, ipadx=10, padx=(0, 6))
        se.insert(0, "Search members...")
        se.bind("<FocusIn>",
                lambda e: se.delete(0, "end")
                if se.get() == "Search members..." else None)
        se.bind("<KeyRelease>",
                lambda e: self._load_members(self._sv.get()))

        # Action buttons
        for text, cmd, bg in [
            ("Add Member",    self._add_member_form,  BTN_COLOR),
            ("Edit Member",   self._edit_member_form, CARD_COLOR),
            ("Delete Member", self._delete_member,    "#c0392b"),
            ("Check-In",      self._record_checkin,   "#27ae60"),
        ]:
            btn(top, text, cmd, bg=bg).pack(side="left", padx=3)

        # Members table
        cols = ["ID", "Full Name", "Username", "Email",
                "Phone", "Plan", "Status", "Expires"]
        self.mtree, tf = make_table(f, cols, 16)
        tf.pack(fill="both", expand=True)

        # Set custom column widths
        for col, w in zip(cols, [40, 150, 110, 170, 110, 90, 80, 100]):
            self.mtree.column(col, width=w)

        self._load_members()

    def _load_members(self, kw=""):
        """
        Clears and reloads the members table.
        If kw is provided and is not the placeholder text,
        runs a search query; otherwise loads all members.

        Parameters:
            kw — search keyword (default empty = show all)
        """
        for r in self.mtree.get_children():
            self.mtree.delete(r)

        data = (
            self.user.search_members(kw)
            if kw and kw != "Search members..."
            else self.user.get_all_members()
        )

        for m in data:
            self.mtree.insert("", "end", values=(
                m["id"], m["full_name"], m["username"],
                m["email"] or "", m["phone"] or "",
                m["membership_plan"], m["status"],
                m["membership_end"] or "N/A"))

    def _selected(self, tree):
        """
        Returns the values tuple of the selected row in a table,
        or None if nothing is selected.
        Used by all delete/edit methods before acting on a row.
        """
        sel = tree.selection()
        return tree.item(sel[0])["values"] if sel else None

    def _add_member_form(self):
        """
        Opens a popup form to create a new member account.
        Creates both a users row (login credentials) and a
        members row (profile + membership details).
        The membership end date is auto-calculated from the
        selected plan's duration.
        """
        # FIX: increased height from original to show Save/Cancel buttons
        win = popup(self.root, "Add Member", 450, 640)
        popup_header(win, "Add New Member")

        # Build all input fields in one loop
        fields = {}
        for k, lb, sh in [
            ("full_name", "Full Name", ""),
            ("username",  "Username",  ""),
            ("password",  "Password",  "*"),
            ("email",     "Email",     ""),
            ("phone",     "Phone",     ""),
        ]:
            fields[k] = form_row(win, lb, show=sh)

        # Plan dropdown populated from the database
        plans = self.user.get_all_plans()
        lbl(win, "Membership Plan", 9,
            color=SUBTEXT_COLOR, bg=CARD_COLOR).pack(anchor="w", padx=22)
        pcb, pvar = dropdown(win, [p["plan_name"] for p in plans])
        pcb.pack(fill="x", padx=22, ipady=6, pady=(2, 10))

        # Start date field (defaults to today)
        lbl(win, "Start Date (YYYY-MM-DD)", 9,
            color=SUBTEXT_COLOR, bg=CARD_COLOR).pack(anchor="w", padx=22)
        svar = tk.StringVar(value=str(date.today()))
        tk.Entry(
            win, textvariable=svar, font=("Arial", 11),
            bg=INPUT_BG, fg=TEXT_COLOR,
            insertbackground=TEXT_COLOR, relief="flat"
        ).pack(fill="x", padx=22, ipady=7, pady=(2, 14))

        def save():
            """Validates form and saves the new member to the database."""
            d = {k: e.var.get().strip() for k, e in fields.items()}

            if not all([d["full_name"], d["username"], d["password"]]):
                messagebox.showerror(
                    "Error",
                    "Name, username and password are required.",
                    parent=win)
                return

            # Auto-calculate end date from plan duration
            sel_plan = next(
                (p for p in plans if p["plan_name"] == pvar.get()),
                None)
            try:
                sd  = date.fromisoformat(svar.get().strip())
                end = str(sd + relativedelta(
                    months=sel_plan["duration_months"]))
            except Exception:
                messagebox.showerror(
                    "Error", "Invalid date format.", parent=win)
                return

            ok, msg = self.user.add_member(
                d["username"], d["password"], d["full_name"],
                d["email"], d["phone"], pvar.get(), str(sd), end)

            if ok:
                messagebox.showinfo("Success", msg, parent=win)
                win.destroy()
                self._load_members()
            else:
                messagebox.showerror("Error", msg, parent=win)

        btn(win, "Save Member", save).pack(fill="x", padx=22, pady=6)
        btn(win, "Cancel", win.destroy,
            bg=CARD_COLOR, fg=TEXT_COLOR).pack(fill="x", padx=22)

    def _edit_member_form(self):
        """
        Opens a popup pre-filled with the selected member's data.
        Allows editing name, email, phone, plan and status.
        Updates both the users and members tables on save.
        """
        vals = self._selected(self.mtree)
        if not vals:
            messagebox.showwarning("Warning", "Select a member first.")
            return

        # Unpack selected row values
        uid, name, _, email, phone, plan, status = (
            vals[0], vals[1], vals[2],
            vals[3], vals[4], vals[5], vals[6])

        win = popup(self.root, "Edit Member", 440, 460)
        popup_header(win, "Edit Member")

        # Pre-fill fields with existing data
        fn = form_row(win, "Full Name", value=name)
        em = form_row(win, "Email",     value=email)
        ph = form_row(win, "Phone",     value=phone)

        lbl(win, "Plan", 9,
            color=SUBTEXT_COLOR, bg=CARD_COLOR).pack(anchor="w", padx=22)
        pcb, pvar = dropdown(
            win, [p["plan_name"] for p in self.user.get_all_plans()],
            plan)
        pcb.pack(fill="x", padx=22, ipady=6, pady=(2, 10))

        lbl(win, "Status", 9,
            color=SUBTEXT_COLOR, bg=CARD_COLOR).pack(anchor="w", padx=22)
        scb, svar = dropdown(
            win, ["Active", "Inactive", "Suspended"], status)
        scb.pack(fill="x", padx=22, ipady=6, pady=(2, 14))

        def save():
            """Validates and saves edits to the database."""
            if not fn.var.get().strip():
                messagebox.showerror(
                    "Error", "Name required.", parent=win)
                return

            conn = self.user._db.get_connection()
            cur  = conn.cursor()

            # Update user account details
            cur.execute(
                "UPDATE users SET full_name=?, email=?, phone=?"
                " WHERE id=?",
                (fn.var.get().strip(), em.var.get().strip(),
                 ph.var.get().strip(), uid))

            # Update membership plan and status
            cur.execute(
                "UPDATE members SET membership_plan=?, status=?"
                " WHERE user_id=?",
                (pvar.get(), svar.get(), uid))

            conn.commit()
            conn.close()

            messagebox.showinfo("Saved", "Member updated!", parent=win)
            win.destroy()
            self._load_members()

        btn(win, "Save Changes", save).pack(fill="x", padx=22, pady=6)
        btn(win, "Cancel", win.destroy,
            bg=CARD_COLOR, fg=TEXT_COLOR).pack(fill="x", padx=22)

    def _delete_member(self):
        """
        Deletes the selected member after confirmation.
        Removes both the users row and the members row.
        """
        vals = self._selected(self.mtree)
        if not vals:
            messagebox.showwarning("Warning", "Select a member first.")
            return

        if messagebox.askyesno(
                "Delete",
                f"Delete '{vals[1]}'? This cannot be undone."):
            self.user.delete_member(vals[0])
            self._load_members()

    def _record_checkin(self):
        """
        Records a gym check-in for the selected member.
        Inserts a row into the attendance table with the
        current timestamp.
        """
        vals = self._selected(self.mtree)
        if not vals:
            messagebox.showwarning("Warning", "Select a member first.")
            return

        conn = self.user._db.get_connection()
        cur  = conn.cursor()

        # Look up the member_id from the user_id
        cur.execute(
            "SELECT id FROM members WHERE user_id=?", (vals[0],))
        row = cur.fetchone()

        if row:
            cur.execute(
                "INSERT INTO attendance (member_id) VALUES (?)",
                (row["id"],))
            conn.commit()
            messagebox.showinfo(
                "Check-In", f"{vals[1]} checked in.")

        conn.close()

    # ── Trainers section ──────────────────────────────────────

    def show_trainers(self):
        """
        Displays the trainer management screen with a table
        of all trainers and Add / Delete action buttons.
        """
        self._clear()
        self._set_nav("Trainers")
        f = self._frame()

        header(f, "Trainer Management",
               "Manage gym trainers").pack(fill="x", pady=(0, 14))

        top = tk.Frame(f, bg=BG_COLOR)
        top.pack(fill="x", pady=(0, 10))
        btn(top, "Add Trainer",
            self._add_trainer_form).pack(side="left", padx=3)
        btn(top, "Delete Trainer",
            self._delete_trainer, bg="#c0392b").pack(side="left", padx=3)

        cols = ["ID", "Full Name", "Email",
                "Phone", "Specialty", "Hired", "Status"]
        self.ttree, tf = make_table(f, cols, 16)
        tf.pack(fill="both", expand=True)
        self._load_trainers()

    def _load_trainers(self):
        """Clears and reloads the trainers table from the database."""
        for r in self.ttree.get_children():
            self.ttree.delete(r)
        for t in self.user.get_all_trainers():
            self.ttree.insert("", "end", values=(
                t["id"], t["full_name"], t["email"] or "",
                t["phone"] or "", t["specialty"] or "",
                t["hire_date"] or "", t["status"]))

    def _add_trainer_form(self):
        """Opens a popup form to add a new trainer record."""
        # FIX: increased height from 360 to 460 to show Save/Cancel buttons
        win = popup(self.root, "Add Trainer", 420, 460)
        popup_header(win, "Add New Trainer")

        fn = form_row(win, "Full Name")
        em = form_row(win, "Email")
        ph = form_row(win, "Phone")
        sp = form_row(win, "Specialty")

        def save():
            if not fn.var.get().strip():
                messagebox.showerror(
                    "Error", "Name required.", parent=win)
                return
            self.user.add_trainer(
                fn.var.get().strip(), em.var.get().strip(),
                ph.var.get().strip(), sp.var.get().strip())
            messagebox.showinfo("Success", "Trainer added!", parent=win)
            win.destroy()
            self._load_trainers()

        btn(win, "Save Trainer", save).pack(fill="x", padx=22, pady=8)
        btn(win, "Cancel", win.destroy,
            bg=CARD_COLOR, fg=TEXT_COLOR).pack(fill="x", padx=22)

    def _delete_trainer(self):
        """Deletes the selected trainer after confirmation."""
        vals = self._selected(self.ttree)
        if not vals:
            messagebox.showwarning("Warning", "Select a trainer.")
            return

        if messagebox.askyesno("Delete", f"Delete '{vals[1]}'?"):
            conn = self.user._db.get_connection()
            conn.cursor().execute(
                "DELETE FROM trainers WHERE id=?", (vals[0],))
            conn.commit()
            conn.close()
            self._load_trainers()

    # ── Plans section ─────────────────────────────────────────

    def show_plans(self):
        """Displays the membership plans management screen."""
        self._clear()
        self._set_nav("Plans")
        f = self._frame()

        header(f, "Membership Plans",
               "Create and manage subscription plans").pack(
            fill="x", pady=(0, 14))

        top = tk.Frame(f, bg=BG_COLOR)
        top.pack(fill="x", pady=(0, 10))
        btn(top, "Add Plan",
            self._add_plan_form).pack(side="left", padx=3)
        btn(top, "Delete Plan",
            self._delete_plan, bg="#c0392b").pack(side="left", padx=3)

        cols = ["ID", "Plan Name", "Months",
                "Price (KES)", "Description"]
        self.ptree, tf = make_table(f, cols, 14)
        tf.pack(fill="both", expand=True)
        self.ptree.column("Description", width=280)
        self._load_plans()

    def _load_plans(self):
        """Clears and reloads the plans table from the database."""
        for r in self.ptree.get_children():
            self.ptree.delete(r)
        for p in self.user.get_all_plans():
            self.ptree.insert("", "end", values=(
                p["id"], p["plan_name"],
                p["duration_months"],
                f"{p['price']:,.0f}",
                p["description"] or ""))

    def _add_plan_form(self):
        """Opens a popup form to add a new membership plan."""
        # FIX: increased height from 340 to 440 to show Save/Cancel buttons
        win = popup(self.root, "Add Plan", 420, 440)
        popup_header(win, "Add Membership Plan")

        nm = form_row(win, "Plan Name")
        dr = form_row(win, "Duration (months)")
        pr = form_row(win, "Price (KES)")
        ds = form_row(win, "Description")

        def save():
            if not all([nm.var.get().strip(),
                        dr.var.get().strip(),
                        pr.var.get().strip()]):
                messagebox.showerror(
                    "Error", "All fields required.", parent=win)
                return
            try:
                conn = self.user._db.get_connection()
                conn.cursor().execute(
                    "INSERT INTO membership_plans"
                    " (plan_name, duration_months, price, description)"
                    " VALUES (?, ?, ?, ?)",
                    (nm.var.get().strip(), int(dr.var.get()),
                     float(pr.var.get()), ds.var.get().strip()))
                conn.commit()
                conn.close()
                messagebox.showinfo(
                    "Success", "Plan added!", parent=win)
                win.destroy()
                self._load_plans()
            except Exception as ex:
                messagebox.showerror("Error", str(ex), parent=win)

        btn(win, "Save Plan", save).pack(fill="x", padx=22, pady=8)
        btn(win, "Cancel", win.destroy,
            bg=CARD_COLOR, fg=TEXT_COLOR).pack(fill="x", padx=22)

    def _delete_plan(self):
        """Deletes the selected membership plan after confirmation."""
        vals = self._selected(self.ptree)
        if not vals:
            messagebox.showwarning("Warning", "Select a plan.")
            return

        if messagebox.askyesno("Delete", f"Delete plan '{vals[1]}'?"):
            conn = self.user._db.get_connection()
            conn.cursor().execute(
                "DELETE FROM membership_plans WHERE id=?", (vals[0],))
            conn.commit()
            conn.close()
            self._load_plans()

    # ── Payments section ──────────────────────────────────────

    def show_payments(self):
        """Displays the payment records screen."""
        self._clear()
        self._set_nav("Payments")
        f = self._frame()

        header(f, "Payments",
               "Record and track member payments").pack(
            fill="x", pady=(0, 14))

        btn(f, "Record Payment",
            self._add_payment_form).pack(anchor="w", pady=(0, 10))

        cols = ["ID", "Member", "Amount (KES)",
                "Plan", "Date", "Method", "Status"]
        self.paytree, tf = make_table(f, cols, 16)
        tf.pack(fill="both", expand=True)
        self._load_payments()

    def _load_payments(self):
        """Clears and reloads the payments table."""
        for r in self.paytree.get_children():
            self.paytree.delete(r)
        for p in self.user.get_all_payments():
            self.paytree.insert("", "end", values=(
                p["id"], p["full_name"],
                f"{p['amount']:,.0f}",
                p["plan_name"] or "",
                p["payment_date"],
                p["payment_method"],
                p["status"]))

    def _add_payment_form(self):
        """
        Opens a popup to record a new payment.
        Lets admin select member, enter amount,
        choose plan and payment method.
        """
        # FIX: increased height from 380 to 500 to show Save/Cancel buttons
        win = popup(self.root, "Record Payment", 420, 500)
        popup_header(win, "Record Payment")

        members = self.user.get_all_members()
        # Map full name -> member_id for easy lookup on save
        mmap = {m["full_name"]: m["member_id"] for m in members}

        lbl(win, "Member", 9,
            color=SUBTEXT_COLOR, bg=CARD_COLOR).pack(anchor="w", padx=22)
        mcb, mvar = dropdown(win, list(mmap.keys()))
        mcb.pack(fill="x", padx=22, ipady=6, pady=(2, 10))

        am = form_row(win, "Amount (KES)")

        lbl(win, "Plan", 9,
            color=SUBTEXT_COLOR, bg=CARD_COLOR).pack(anchor="w", padx=22)
        pcb, pvar = dropdown(
            win, [p["plan_name"] for p in self.user.get_all_plans()])
        pcb.pack(fill="x", padx=22, ipady=6, pady=(2, 10))

        lbl(win, "Payment Method", 9,
            color=SUBTEXT_COLOR, bg=CARD_COLOR).pack(anchor="w", padx=22)
        xcb, xvar = dropdown(
            win, ["Cash", "M-Pesa", "Card", "Bank Transfer"])
        xcb.pack(fill="x", padx=22, ipady=6, pady=(2, 14))

        def save():
            if not mvar.get() or not am.var.get().strip():
                messagebox.showerror(
                    "Error", "Member and amount required.", parent=win)
                return
            self.user.add_payment(
                mmap[mvar.get()], float(am.var.get()),
                pvar.get(), xvar.get())
            messagebox.showinfo(
                "Success", "Payment recorded!", parent=win)
            win.destroy()
            self._load_payments()

        btn(win, "Save Payment", save).pack(fill="x", padx=22, pady=6)
        btn(win, "Cancel", win.destroy,
            bg=CARD_COLOR, fg=TEXT_COLOR).pack(fill="x", padx=22)

    # ── Attendance section ────────────────────────────────────

    def show_attendance(self):
        """
        Displays a read-only table of all member check-ins,
        ordered most recent first.
        """
        self._clear()
        self._set_nav("Attendance")
        f = self._frame()

        header(f, "Attendance Records",
               "All member check-ins").pack(fill="x", pady=(0, 14))

        cols = ["ID", "Member", "Check-In", "Check-Out"]
        tree, tf = make_table(f, cols, 18)
        tf.pack(fill="both", expand=True)

        for rec in self.user.get_all_attendance():
            tree.insert("", "end", values=(
                rec["id"], rec["full_name"],
                rec["check_in"],
                rec["check_out"] or "Still In"))

    # ── Workouts section ──────────────────────────────────────

    def show_workouts(self):
        """
        Displays assigned workout plans with an option
        to assign a new plan to any member.
        """
        self._clear()
        self._set_nav("Workouts")
        f = self._frame()

        header(f, "Workout Plans",
               "Assign workout plans to members").pack(
            fill="x", pady=(0, 14))

        btn(f, "Assign Plan",
            self._assign_workout_form).pack(anchor="w", pady=(0, 10))

        cols = ["ID", "Member", "Plan Name", "Exercises", "Date"]
        self.wtree, tf = make_table(f, cols, 16)
        tf.pack(fill="both", expand=True)
        self.wtree.column("Exercises", width=280)
        self._load_workouts()

    def _load_workouts(self):
        """
        Loads all workout plans from the database using a
        JOIN across workout_plans, members, and users tables.
        """
        for r in self.wtree.get_children():
            self.wtree.delete(r)

        conn = self.user._db.get_connection()
        cur  = conn.cursor()
        cur.execute("""
            SELECT w.id, u.full_name, w.plan_name,
                   w.exercises, w.created_at
            FROM workout_plans w
            JOIN members m ON w.member_id = m.id
            JOIN users   u ON m.user_id   = u.id
            ORDER BY w.created_at DESC
        """)
        for r in cur.fetchall():
            self.wtree.insert("", "end", values=(
                r["id"], r["full_name"], r["plan_name"],
                r["exercises"] or "", r["created_at"]))
        conn.close()

    def _assign_workout_form(self):
        """
        Opens a popup to assign a workout plan to a member.
        Admin selects a member, enters a plan name, and
        describes the exercises in a multi-line text area.
        """
        win = popup(self.root, "Assign Workout", 460, 420)
        popup_header(win, "Assign Workout Plan")

        members = self.user.get_all_members()
        mmap    = {m["full_name"]: m["member_id"] for m in members}

        lbl(win, "Select Member", 9,
            color=SUBTEXT_COLOR, bg=CARD_COLOR).pack(anchor="w", padx=22)
        mcb, mvar = dropdown(win, list(mmap.keys()))
        mcb.pack(fill="x", padx=22, ipady=6, pady=(2, 10))

        pn = form_row(win, "Plan Name")

        lbl(win, "Exercises", 9,
            color=SUBTEXT_COLOR, bg=CARD_COLOR).pack(anchor="w", padx=22)
        # Multi-line text area for exercise description
        ex = tk.Text(
            win, height=6, font=("Arial", 11),
            bg=INPUT_BG, fg=TEXT_COLOR,
            insertbackground=TEXT_COLOR, relief="flat")
        ex.pack(fill="x", padx=22, pady=(4, 14))

        def save():
            if not mvar.get() or not pn.var.get().strip():
                messagebox.showerror(
                    "Error",
                    "Member and plan name required.", parent=win)
                return
            conn = self.user._db.get_connection()
            conn.cursor().execute(
                "INSERT INTO workout_plans"
                " (member_id, plan_name, exercises, assigned_by)"
                " VALUES (?, ?, ?, ?)",
                (mmap[mvar.get()], pn.var.get().strip(),
                 ex.get("1.0", "end").strip(),
                 self.user.user_id))
            conn.commit()
            conn.close()
            messagebox.showinfo(
                "Success", "Workout assigned!", parent=win)
            win.destroy()
            self._load_workouts()

        btn(win, "Assign Plan", save).pack(
            fill="x", padx=22, pady=4)
        btn(win, "Cancel", win.destroy,
            bg=CARD_COLOR, fg=TEXT_COLOR).pack(fill="x", padx=22)

    # ── Analytics section ─────────────────────────────────────

    def show_analytics(self):
        """
        Displays a summary analytics screen with:
          - Six stat cards (totals and averages)
          - Members grouped by plan (table)
          - Revenue grouped by month (table)
        All data is fetched live from the database.
        """
        self._clear()
        self._set_nav("Analytics")
        f = self._frame()

        header(f, "Analytics & Reports",
               "Gym performance summary").pack(fill="x", pady=(0, 18))

        conn = self.user._db.get_connection()
        cur  = conn.cursor()

        # Helper to run a single-value query and return the result
        def q(sql):
            cur.execute(sql)
            return cur.fetchone()[0]

        # Stat cards data
        stats = [
            ("Total Members",
             q("SELECT COUNT(*) FROM members"),
             ACCENT_COLOR),
            ("Active Members",
             q("SELECT COUNT(*) FROM members WHERE status='Active'"),
             SUCCESS_COLOR),
            ("All-Time Revenue",
             f"KES {q('SELECT COALESCE(SUM(amount),0) FROM payments'):,.0f}",
             WARNING_COLOR),
            ("Total Check-ins",
             q("SELECT COUNT(*) FROM attendance"),
             "#9b59b6"),
            ("Avg BMI",
             q("SELECT ROUND(AVG(bmi),1) FROM fitness_progress"
               " WHERE bmi > 0") or "N/A",
             "#1abc9c"),
            ("Workout Plans",
             q("SELECT COUNT(*) FROM workout_plans"),
             "#e67e22"),
        ]

        # Render stat cards in a row
        row = tk.Frame(f, bg=BG_COLOR)
        row.pack(fill="x", pady=(0, 18))
        for i, (title, val, color) in enumerate(stats):
            c = tk.Frame(row, bg=CARD_COLOR, padx=14, pady=12)
            c.grid(row=0, column=i, padx=5, sticky="ew")
            row.columnconfigure(i, weight=1)
            lbl(c, str(val), 15, bold=True,
                color=color, bg=CARD_COLOR).pack(anchor="w")
            lbl(c, title, 8,
                color=SUBTEXT_COLOR, bg=CARD_COLOR).pack(anchor="w")

        # Two side-by-side breakdown tables
        row2 = tk.Frame(f, bg=BG_COLOR)
        row2.pack(fill="both", expand=True)
        row2.columnconfigure(0, weight=1)
        row2.columnconfigure(1, weight=1)

        # Left — members grouped by plan
        left = tk.Frame(row2, bg=BG_COLOR)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        lbl(left, "Members by Plan", 11, bold=True).pack(
            anchor="w", pady=(0, 6))
        t1, f1 = make_table(left, ["Plan", "Members"], 6)
        f1.pack(fill="both", expand=True)
        cur.execute(
            "SELECT membership_plan, COUNT(*) c FROM members"
            " GROUP BY membership_plan ORDER BY c DESC")
        for r in cur.fetchall():
            t1.insert("", "end",
                      values=(r["membership_plan"], r["c"]))

        # Right — monthly revenue breakdown
        right = tk.Frame(row2, bg=BG_COLOR)
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        lbl(right, "Revenue by Month", 11, bold=True).pack(
            anchor="w", pady=(0, 6))
        t2, f2 = make_table(
            right, ["Month", "Revenue (KES)", "Transactions"], 6)
        f2.pack(fill="both", expand=True)
        cur.execute("""
            SELECT strftime('%Y-%m', payment_date) m,
                   ROUND(SUM(amount), 0)           r,
                   COUNT(*)                        c
            FROM payments
            GROUP BY m ORDER BY m DESC LIMIT 8
        """)
        for r in cur.fetchall():
            t2.insert("", "end",
                      values=(r["m"], f"{r['r']:,.0f}", r["c"]))

        conn.close()

    # ── Logout ────────────────────────────────────────────────

    def logout(self):
        """
        Asks for confirmation, then destroys the dashboard window
        and relaunches a fresh login screen.
        """
        if messagebox.askyesno("Logout", "Are you sure?"):
            self.root.destroy()
            import tkinter as tk
            from gui.login_screen import LoginScreen
            r = tk.Tk()
            LoginScreen(r)
            r.mainloop()
