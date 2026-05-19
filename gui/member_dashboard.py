import tkinter as tk
from tkinter import messagebox
from gui.components import (
    SidebarButton, make_table, header, card,
    form_row, btn, lbl,
    BG_COLOR, SIDEBAR_COLOR, CARD_COLOR, ACCENT_COLOR,
    TEXT_COLOR, SUBTEXT_COLOR, SUCCESS_COLOR,
    WARNING_COLOR, INPUT_BG
)
# from chatbot.chatbot import Chatbot
from datetime import date
import random


class MemberDashboard:
    """
    The member dashboard window.

    Receives a Member model instance (self.user) which provides
    all database reads and writes scoped to that member only.
    Also holds a Chatbot instance for the FitBot chat section.
    """

    def __init__(self, root, user):
        """
        Initialises the dashboard and builds the layout.

        Parameters:
            root — the Toplevel window opened after login
            user — a Member model instance
        """
        self.root    = root
        self.user    = user
        self.logout_callback = None
        # self.chatbot = Chatbot()   # FitBot assistant instance

        self.root.title("SmartFit  -  Member Dashboard")
        self.root.geometry("1100x700")
        self.root.configure(bg=BG_COLOR)

        # Centre window on screen
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        self.root.geometry(
            f"1100x700+{(sw - 1100) // 2}+{(sh - 700) // 2}")

        self._build_layout()
        self.show_home()   # load Home section on start

    # ── Layout builders ───────────────────────────────────────

    def _build_layout(self):
        """
        Creates the two-column layout:
          Left  — sidebar (fixed width)
          Right — content area (expands to fill)
        """
        self.sidebar = tk.Frame(
            self.root, bg=SIDEBAR_COLOR, width=210)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.content = tk.Frame(self.root, bg=BG_COLOR)
        self.content.pack(side="right", fill="both", expand=True)

        self._build_sidebar()

    def _build_sidebar(self):
        """
        Populates the sidebar with:
          - App name and Member Portal label
          - Member name and status badge
          - Navigation buttons
          - Logout button pinned to the bottom
        """
        # Logo area
        logo = tk.Frame(self.sidebar, bg=ACCENT_COLOR, pady=16)
        logo.pack(fill="x")
        tk.Label(
            logo, text="SMARTFIT",
            font=("Arial", 15, "bold"),
            bg=ACCENT_COLOR, fg="white"
        ).pack()
        tk.Label(
            logo, text="Member Portal",
            font=("Arial", 9),
            bg=ACCENT_COLOR, fg="#ffd0d8"
        ).pack()

        # Member name
        status = getattr(self.user, "status", "Active")
        lbl(self.sidebar, self.user.full_name, 9,
            color=SUBTEXT_COLOR, bg=SIDEBAR_COLOR,
            wraplength=190).pack(pady=(10, 2))

        # Status badge — green if active, red if not
        lbl(self.sidebar, f"{status} Member", 9, bold=True,
            color=SUCCESS_COLOR if status == "Active" else ACCENT_COLOR,
            bg=SIDEBAR_COLOR).pack(pady=(0, 6))

        tk.Frame(self.sidebar, bg=CARD_COLOR, height=1).pack(
            fill="x", padx=14, pady=4)

        # Navigation items
        nav = [
            ("Home",         self.show_home),
            ("My Profile",   self.show_profile),
            ("Membership",   self.show_membership),
            ("Workout Plan", self.show_workout),
            ("Attendance",   self.show_attendance),
            ("My Progress",  self.show_progress),
            ("FitBot Chat",  self.show_chatbot),
        ]
        self.nav_btns = {}
        for name, cmd in nav:
            b = SidebarButton(self.sidebar, name, cmd)
            b.pack(fill="x", padx=6, pady=2)
            self.nav_btns[name] = b

        # Logout pinned to bottom
        tk.Frame(self.sidebar, bg=CARD_COLOR, height=1).pack(
            fill="x", padx=14, pady=4, side="bottom")
        btn(self.sidebar, "Logout", self.logout,
            bg="#c0392b").pack(fill="x", padx=6, pady=8, side="bottom")

    # ── Navigation helpers ────────────────────────────────────

    def _set_nav(self, name):
        """Highlights the active nav button, resets all others."""
        for k, b in self.nav_btns.items():
            b.set_active() if k == name else b.set_inactive()

    def _rebuild_sidebar(self):
        """
        Destroys and rebuilds the sidebar so the status badge
        reflects the latest value from self.user after a profile
        change (e.g. membership cancellation or reactivation).
        Nav button highlight is restored for the current section.
        """
        # Remember which nav button is currently active
        active = next(
            (k for k, b in self.nav_btns.items()
             if b.cget("bg") == ACCENT_COLOR),
            None)

        # Destroy all sidebar widgets and rebuild from scratch
        for w in self.sidebar.winfo_children():
            w.destroy()

        self._build_sidebar()

        # Restore the active highlight
        if active and active in self.nav_btns:
            self.nav_btns[active].set_active()

    def _clear(self):
        """Clears all widgets from the content area."""
        for w in self.content.winfo_children():
            w.destroy()

    def _frame(self):
        """Returns a new padded content frame."""
        f = tk.Frame(self.content, bg=BG_COLOR, padx=24, pady=20)
        f.pack(fill="both", expand=True)
        return f

    # ── Home section ──────────────────────────────────────────

    def show_home(self):
        """
        Displays the member home screen with:
          - Welcome greeting and today's date
          - Three quick-info cards (plan, status, expiry)
          - Quick check-in button
          - A randomly chosen motivational quote
        """
        self._clear()
        self._set_nav("Home")
        f = self._frame()

        first_name = self.user.full_name.split()[0]
        header(f, f"Welcome back, {first_name}",
               date.today().strftime("%A, %B %d, %Y")).pack(
            fill="x", pady=(0, 18))

        # Quick-info cards row
        row = tk.Frame(f, bg=BG_COLOR)
        row.pack(fill="x", pady=(0, 16))

        # When inactive, hide plan and expiry so the home screen
        # is not misleading — member should contact admin to reactivate
        _status  = getattr(self.user, "status", "Active")
        _plan    = (getattr(self.user, "membership_plan", "None")
                    if _status == "Active" else "None")
        _expires = (getattr(self.user, "membership_end", "N/A") or "N/A"
                    if _status == "Active" else "N/A")

        for i, (title, val, color) in enumerate([
            ("My Plan",
             _plan,
             WARNING_COLOR if _status == "Active" else SUBTEXT_COLOR),
            ("Status",
             _status,
             SUCCESS_COLOR if _status == "Active" else ACCENT_COLOR),
            ("Expires",
             _expires,
             "#9b59b6" if _status == "Active" else SUBTEXT_COLOR),
        ]):
            c = card(row)
            c.grid(row=0, column=i, padx=8, sticky="ew")
            row.columnconfigure(i, weight=1)
            lbl(c, str(val), 13, bold=True,
                color=color, bg=CARD_COLOR).pack(anchor="w")
            lbl(c, title, 9,
                color=SUBTEXT_COLOR, bg=CARD_COLOR).pack(anchor="w")

        # Quick check-in card
        ci = card(f); ci.pack(fill="x", pady=(0, 14))
        lbl(ci, "Quick Check-In", 12,
            bold=True, bg=CARD_COLOR).pack(anchor="w")
        lbl(ci, "Record your gym visit for today", 9,
            color=SUBTEXT_COLOR, bg=CARD_COLOR).pack(
            anchor="w", pady=(2, 10))
        btn(ci, "Check In Now",
            self._do_checkin, bg="#27ae60").pack(anchor="w")

        # Random motivational quote card
        quotes = [
            "The only bad workout is the one that didn't happen.",
            "Push yourself because no one else is going to do it for you.",
            "Success starts with self-discipline.",
            "Wake up. Work out. Be happy.",
        ]
        qc = card(f); qc.pack(fill="x")
        lbl(qc, "Daily Motivation", 11, bold=True,
            color=ACCENT_COLOR, bg=CARD_COLOR).pack(anchor="w")
        lbl(qc, f'"{random.choice(quotes)}"', 10,
            bg=CARD_COLOR, wraplength=700).pack(
            anchor="w", pady=(6, 0))

    def _do_checkin(self):
        """
        Calls user.check_in() to insert a row in the attendance
        table, then shows a confirmation message.
        """
        try:
            self.user.check_in()
            messagebox.showinfo(
                "Checked In",
                f"Welcome, {self.user.full_name.split()[0]}!"
                " Check-in recorded.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ── Profile section ───────────────────────────────────────

    def show_profile(self):
        """
        Displays the member profile editor with:
          - Name display (read-only avatar section)
          - Editable name, email, phone fields
          - Optional password change fields
          - Save button that writes changes to the database
          - Delete Account button at the bottom
        """
        self._clear()
        self._set_nav("My Profile")
        f = self._frame()

        header(f, "My Profile",
               "View and update your personal info").pack(
            fill="x", pady=(0, 18))

        c = card(f, padx=28, pady=22)
        c.pack(fill="x")

        # Avatar / name display area
        av = tk.Frame(c, bg=CARD_COLOR)
        av.pack(anchor="w", pady=(0, 14))

        # Placeholder avatar using square brackets as a text icon
        lbl(av, "[  ]", 28, bold=True,
            color=ACCENT_COLOR, bg=CARD_COLOR).pack(side="left")

        inf = tk.Frame(av, bg=CARD_COLOR, padx=12)
        inf.pack(side="left")
        lbl(inf, self.user.full_name, 15,
            bold=True, bg=CARD_COLOR).pack(anchor="w")
        lbl(inf, f"@{self.user.username}", 10,
            color=SUBTEXT_COLOR, bg=CARD_COLOR).pack(anchor="w")
        lbl(inf, "Member", 9,
            color=ACCENT_COLOR, bg=CARD_COLOR).pack(anchor="w")

        tk.Frame(c, bg=INPUT_BG, height=1).pack(fill="x", pady=10)

        # Editable fields in two columns
        row = tk.Frame(c, bg=CARD_COLOR)
        row.pack(fill="x")
        lc = tk.Frame(row, bg=CARD_COLOR)
        lc.pack(side="left", expand=True, fill="x", padx=(0, 14))
        rc = tk.Frame(row, bg=CARD_COLOR)
        rc.pack(side="left", expand=True, fill="x")

        self._fn = form_row(lc, "Full Name", value=self.user.full_name)
        self._em = form_row(lc, "Email",     value=self.user.email or "")
        self._ph = form_row(rc, "Phone",     value=self.user.phone or "")

        tk.Frame(c, bg=INPUT_BG, height=1).pack(fill="x", pady=10)
        lbl(c, "Change Password", 11,
            bold=True, bg=CARD_COLOR).pack(anchor="w")

        # Password change fields (optional — only applied if filled in)
        pr = tk.Frame(c, bg=CARD_COLOR)
        pr.pack(fill="x", pady=(6, 0))
        self._pw  = form_row(pr, "New Password",     show="*")
        self._pw2 = form_row(pr, "Confirm Password", show="*")

        # Save and Delete Account buttons side by side
        btn_row = tk.Frame(c, bg=CARD_COLOR)
        btn_row.pack(anchor="w", pady=(14, 0))

        btn(btn_row, "Save Changes",
            self._save_profile).pack(side="left", padx=(0, 10))

        btn(btn_row, "Delete Account",
            self._delete_account, bg="#c0392b").pack(side="left")

    def _save_profile(self):
        """
        Reads the profile form fields and saves changes.
        Updates name, email, phone via user.update_profile().
        If the password fields are filled, also calls
        user.change_password() after confirming they match.
        """
        name = self._fn.var.get().strip()
        if not name:
            messagebox.showerror("Error", "Name cannot be empty.")
            return

        self.user.update_profile(
            name,
            self._em.var.get().strip(),
            self._ph.var.get().strip())

        pw = self._pw.var.get().strip()
        if pw:
            if pw != self._pw2.var.get().strip():
                messagebox.showerror("Error", "Passwords do not match.")
                return
            if len(pw) < 6:
                messagebox.showerror(
                    "Error", "Password must be 6+ characters.")
                return
            self.user.change_password(pw)

        messagebox.showinfo("Saved", "Profile updated.")

    def _delete_account(self):
        """
        Asks for confirmation twice before permanently deleting
        the member's account, all attendance records, progress
        entries, and workout plans from the database.
        After deletion the dashboard closes and the login
        screen is relaunched.
        """
        if not messagebox.askyesno(
                "Delete Account",
                "Are you sure you want to delete your account?\n"
                "This will permanently remove all your data."):
            return

        if not messagebox.askyesno(
                "Final Confirmation",
                "This cannot be undone.\n"
                "Are you absolutely sure?"):
            return

        conn   = self.user._db.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM attendance WHERE member_id=?",
            (self.user.member_id,))
        cursor.execute(
            "DELETE FROM fitness_progress WHERE member_id=?",
            (self.user.member_id,))
        cursor.execute(
            "DELETE FROM workout_plans WHERE member_id=?",
            (self.user.member_id,))
        cursor.execute(
            "DELETE FROM payments WHERE member_id=?",
            (self.user.member_id,))
        cursor.execute(
            "DELETE FROM members WHERE id=?",
            (self.user.member_id,))
        cursor.execute(
            "DELETE FROM users WHERE id=?",
            (self.user.user_id,))

        conn.commit()
        conn.close()

        messagebox.showinfo(
            "Account Deleted",
            "Your account has been deleted.")

        self.root.destroy()
        import tkinter as tk2
        from gui.login_screen import LoginScreen
        r = tk2.Tk()
        LoginScreen(r)
        r.mainloop()

    # ── Membership section ────────────────────────────────────

    def show_membership(self):
        """
        Shows the member's current membership details and allows:
          - Viewing current plan, status, start date, expiry
          - Selecting and upgrading to a different plan
          - Cancelling membership (sets status to Inactive)

        FIX: content is placed inside a scrollable canvas so the
        Upgrade and Cancel buttons are always reachable regardless
        of window height.
        """
        self._clear()
        self._set_nav("Membership")

        # ── Scrollable container ──────────────────────────────
        # Outer frame fills the content area
        outer = tk.Frame(self.content, bg=BG_COLOR)
        outer.pack(fill="both", expand=True)

        # Canvas + vertical scrollbar
        canvas = tk.Canvas(outer, bg=BG_COLOR, highlightthickness=0)
        scrollbar = tk.Scrollbar(
            outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # Inner frame that holds all actual content
        inner = tk.Frame(canvas, bg=BG_COLOR, padx=24, pady=20)
        canvas_window = canvas.create_window(
            (0, 0), window=inner, anchor="nw")

        # Make the inner frame stretch to canvas width
        def _on_canvas_resize(event):
            canvas.itemconfig(canvas_window, width=event.width)

        canvas.bind("<Configure>", _on_canvas_resize)

        # Update scroll region whenever inner frame changes size
        def _on_frame_resize(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        inner.bind("<Configure>", _on_frame_resize)

        # Allow mouse-wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        # Linux scroll support
        canvas.bind_all("<Button-4>",
                        lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>",
                        lambda e: canvas.yview_scroll(1, "units"))

        # f is the inner frame — all content packs into this
        f = inner

        header(f, "My Membership",
               "Current plan and membership details").pack(
            fill="x", pady=(0, 18))

        # Read current values from the member model
        plan   = getattr(self.user, "membership_plan",  "Basic")
        start  = getattr(self.user, "membership_start", "N/A")
        end    = getattr(self.user, "membership_end",   "N/A")
        status = getattr(self.user, "status",           "Active")

        # -- Inactive gate: show contact message and stop here --
        if status == "Inactive":
            inactive_card = card(f, padx=24, pady=28)
            inactive_card.pack(fill="x", pady=(0, 16))

            icon_row = tk.Frame(inactive_card, bg=CARD_COLOR)
            icon_row.pack(anchor="w", pady=(0, 10))
            lbl(icon_row, "X", 22, bold=True,
                color=ACCENT_COLOR, bg=CARD_COLOR).pack(side="left")
            lbl(icon_row, "  Membership Inactive", 15, bold=True,
                color=ACCENT_COLOR, bg=CARD_COLOR).pack(side="left")

            tk.Frame(inactive_card, bg=INPUT_BG, height=1).pack(
                fill="x", pady=(4, 14))

            lbl(inactive_card,
                "Your membership has been cancelled and is currently inactive. "
                "You do not have an active plan at this time.",
                11, color=TEXT_COLOR, bg=CARD_COLOR,
                wraplength=600).pack(anchor="w")

            lbl(inactive_card,
                "To reactivate your membership, please contact the front desk "
                "or visit the gym reception. An admin will restore your access.",
                10, color=SUBTEXT_COLOR, bg=CARD_COLOR,
                wraplength=600).pack(anchor="w", pady=(10, 0))

            # Stop here: do not show plan details or upgrade/cancel cards
            return

        # -- Current plan summary card (Active members only) --
        current = card(f, padx=24, pady=18)
        current.pack(fill="x", pady=(0, 16))

        lbl(current, "Current Plan", 10,
            color=SUBTEXT_COLOR, bg=CARD_COLOR).pack(anchor="w")

        badge = tk.Frame(current, bg=ACCENT_COLOR, padx=14, pady=6)
        badge.pack(anchor="w", pady=(4, 12))
        lbl(badge, f"{plan} Plan", 14,
            bold=True, bg=ACCENT_COLOR, color="white").pack()

        details = tk.Frame(current, bg=CARD_COLOR)
        details.pack(fill="x")

        for i, (label, val) in enumerate([
            ("Status",     status),
            ("Start Date", start  or "N/A"),
            ("Expiry",     end    or "N/A"),
        ]):
            col = tk.Frame(details, bg=CARD_COLOR)
            col.grid(row=0, column=i, padx=(0, 24))
            details.columnconfigure(i, weight=0)
            lbl(col, label, 9,
                color=SUBTEXT_COLOR, bg=CARD_COLOR).pack(anchor="w")
            lbl(col, val, 11, bold=True,
                bg=CARD_COLOR).pack(anchor="w")

        if end and end != "N/A":
            try:
                days  = (date.fromisoformat(end) - date.today()).days
                color = (
                    "#2ecc71"      if days > 7
                    else WARNING_COLOR if days >= 0
                    else ACCENT_COLOR
                )
                text = (
                    f"Expired {abs(days)} days ago"
                    if days < 0
                    else f"{days} days remaining"
                )
                tk.Frame(current, bg=INPUT_BG, height=1).pack(
                    fill="x", pady=(12, 8))
                lbl(current, text, 13, bold=True,
                    color=color, bg=CARD_COLOR).pack(anchor="w")
            except Exception:
                pass


        # ── Change plan card ──────────────────────────────────
        change = card(f, padx=24, pady=18)
        change.pack(fill="x", pady=(0, 16))

        lbl(change, "Change Membership Plan", 12,
            bold=True, bg=CARD_COLOR).pack(anchor="w")
        lbl(change,
            "Select a plan below and click Upgrade to apply it.",
            9, color=SUBTEXT_COLOR, bg=CARD_COLOR).pack(
            anchor="w", pady=(2, 14))

        conn   = self.user._db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM membership_plans ORDER BY price")
        plans = [dict(r) for r in cursor.fetchall()]
        conn.close()

        self._plan_var = tk.StringVar(value=plan)

        plans_frame = tk.Frame(change, bg=CARD_COLOR)
        plans_frame.pack(fill="x", pady=(0, 14))

        for i, p in enumerate(plans):
            row = tk.Frame(plans_frame, bg=INPUT_BG, padx=14, pady=10)
            row.grid(row=i // 2, column=i % 2,
                     padx=6, pady=4, sticky="ew")
            plans_frame.columnconfigure(i % 2, weight=1)

            rb = tk.Radiobutton(
                row,
                variable=self._plan_var,
                value=p["plan_name"],
                bg=INPUT_BG,
                activebackground=INPUT_BG,
                selectcolor=INPUT_BG,
                cursor="hand2"
            )
            rb.pack(side="left")

            info = tk.Frame(row, bg=INPUT_BG)
            info.pack(side="left", padx=(6, 0))

            lbl(info, p["plan_name"], 11,
                bold=True, bg=INPUT_BG).pack(anchor="w")
            lbl(info,
                f"KES {p['price']:,.0f}"
                f"  |  {p['duration_months']} month(s)",
                9, color=SUBTEXT_COLOR, bg=INPUT_BG).pack(anchor="w")
            lbl(info, p["description"] or "", 8,
                color=SUBTEXT_COLOR, bg=INPUT_BG).pack(anchor="w")

        def upgrade():
            selected = self._plan_var.get()

            if selected == plan:
                messagebox.showinfo(
                    "No Change",
                    "You are already on this plan.")
                return

            sel_plan = next(
                (p for p in plans if p["plan_name"] == selected),
                None)
            if not sel_plan:
                return

            from dateutil.relativedelta import relativedelta
            new_start = str(date.today())
            new_end   = str(
                date.today() + relativedelta(
                    months=sel_plan["duration_months"]))

            conn   = self.user._db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE members
                SET membership_plan  = ?,
                    membership_start = ?,
                    membership_end   = ?,
                    status           = 'Active'
                WHERE id = ?
            """, (selected, new_start, new_end,
                  self.user.member_id))
            conn.commit()
            conn.close()

            self.user.load_member_profile()

            # Rebuild sidebar so the status badge stays in sync
            self._rebuild_sidebar()

            messagebox.showinfo(
                "Plan Updated",
                f"Your plan has been changed to {selected}.\n"
                f"New expiry: {new_end}")

            self.show_membership()

        btn(change, "Upgrade / Change Plan",
            upgrade).pack(anchor="w")

        # ── Cancel membership card ────────────────────────────
        cancel_card = card(f, padx=24, pady=16)
        cancel_card.pack(fill="x", pady=(0, 20))

        lbl(cancel_card, "Cancel Membership", 12,
            bold=True, bg=CARD_COLOR).pack(anchor="w")
        lbl(cancel_card,
            "Cancelling sets your status to Inactive immediately.\n"
            "You can reactivate by contacting the front desk.",
            9, color=SUBTEXT_COLOR, bg=CARD_COLOR).pack(
            anchor="w", pady=(4, 12))

        def cancel():
            if status == "Inactive":
                messagebox.showinfo(
                    "Already Inactive",
                    "Your membership is already cancelled.")
                return

            if not messagebox.askyesno(
                    "Cancel Membership",
                    "Are you sure you want to cancel your membership?\n"
                    "Your account will be set to Inactive."):
                return

            conn   = self.user._db.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE members SET status = 'Inactive' WHERE id = ?",
                (self.user.member_id,))
            conn.commit()
            conn.close()

            self.user.load_member_profile()

            # Rebuild sidebar so the status badge updates immediately
            self._rebuild_sidebar()

            messagebox.showinfo(
                "Membership Cancelled",
                "Your membership has been cancelled.\n"
                "Contact the front desk to reactivate.")

            self.show_membership()

        btn(cancel_card, "Cancel Membership",
            cancel, bg="#c0392b").pack(anchor="w")

    # ── Workout section ───────────────────────────────────────

    def show_workout(self):
        """
        Shows the member's assigned workout plan.
        If no plan is assigned yet, shows a message and a
        button to open FitBot for workout suggestions instead.
        """
        self._clear()
        self._set_nav("Workout Plan")
        f = self._frame()

        header(f, "My Workout Plan",
               "Your trainer-assigned routine").pack(
            fill="x", pady=(0, 18))

        plan = self.user.get_workout_plan()

        if not plan:
            c = card(f, padx=28, pady=28)
            c.pack(fill="x")
            lbl(c, "No workout plan assigned yet", 13,
                bold=True, bg=CARD_COLOR).pack(pady=(8, 4))
            lbl(c, "Ask your trainer or admin to assign a plan.", 10,
                color=SUBTEXT_COLOR, bg=CARD_COLOR).pack()
            btn(c, "Ask FitBot for Ideas",
                self.show_chatbot).pack(pady=(14, 0))
            return

        c = card(f, padx=28, pady=22)
        c.pack(fill="both", expand=True)

        lbl(c, plan["plan_name"], 15,
            bold=True, color=ACCENT_COLOR, bg=CARD_COLOR).pack(
            anchor="w")
        lbl(c, f"Assigned: {plan['created_at']}", 9,
            color=SUBTEXT_COLOR, bg=CARD_COLOR).pack(
            anchor="w", pady=(2, 12))

        tk.Frame(c, bg=INPUT_BG, height=1).pack(fill="x", pady=(0, 10))
        lbl(c, "Exercises:", 11,
            bold=True, bg=CARD_COLOR).pack(anchor="w")

        t = tk.Text(
            c, font=("Arial", 11), bg=INPUT_BG, fg=TEXT_COLOR,
            relief="flat", wrap="word", height=12)
        t.pack(fill="both", expand=True, pady=(8, 0))
        t.insert("1.0", plan.get("exercises", "No details provided."))
        t.config(state="disabled")

    # ── Attendance section ────────────────────────────────────

    def show_attendance(self):
        """
        Shows the member's last 30 check-in records in a table.
        Action buttons:
          - Check In  — adds a new attendance row
          - Check Out — records check-out time on selected row
          - Update    — edit the check-in/out time on selected row
          - Delete    — remove a selected attendance record
        """
        self._clear()
        self._set_nav("Attendance")
        f = self._frame()

        header(f, "Attendance History",
               "Your last 30 gym visits").pack(
            fill="x", pady=(0, 14))

        top = tk.Frame(f, bg=BG_COLOR)
        top.pack(fill="x", pady=(0, 10))

        btn(top, "Check In",
            self._do_checkin, bg="#27ae60").pack(side="left", padx=(0, 6))
        btn(top, "Check Out",
            self._do_checkout, bg="#2980b9").pack(side="left", padx=(0, 6))
        btn(top, "Update Record",
            self._update_attendance, bg=CARD_COLOR,
            fg=TEXT_COLOR).pack(side="left", padx=(0, 6))
        btn(top, "Delete Record",
            self._delete_attendance, bg="#c0392b").pack(side="left")

        cols = ["ID", "#", "Check-In Time", "Check-Out Time"]
        self.att_tree, tf = make_table(f, cols, 16)
        tf.pack(fill="both", expand=True)

        self.att_tree.column("ID", width=0, stretch=False)
        self.att_tree.heading("ID", text="")

        self._load_attendance()

    def _load_attendance(self):
        """
        Clears and reloads the attendance table.
        Fetches the member's last 30 records from the database.
        """
        for r in self.att_tree.get_children():
            self.att_tree.delete(r)

        conn   = self.user._db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, check_in, check_out
            FROM attendance
            WHERE member_id = ?
            ORDER BY check_in DESC
            LIMIT 30
        """, (self.user.member_id,))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            self.att_tree.insert(
                "", "end",
                values=("", "--", "No records yet", "--"))
        else:
            for i, r in enumerate(rows, 1):
                self.att_tree.insert("", "end", values=(
                    r["id"],
                    i,
                    r["check_in"],
                    r["check_out"] or "--"))

    def _get_selected_attendance(self):
        """
        Returns the values of the selected attendance row,
        or None if nothing is selected.
        """
        sel = self.att_tree.selection()
        if not sel:
            messagebox.showwarning(
                "Warning", "Please select a record first.")
            return None
        return self.att_tree.item(sel[0])["values"]

    def _do_checkout(self):
        """
        Records the current time as the check-out time for
        the selected attendance row.
        """
        vals = self._get_selected_attendance()
        if not vals:
            return

        att_id   = vals[0]
        checkout = vals[3]

        if checkout and checkout != "--":
            messagebox.showwarning(
                "Warning",
                "This record already has a check-out time.")
            return

        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn   = self.user._db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE attendance SET check_out=? WHERE id=?",
            (now, att_id))
        conn.commit()
        conn.close()

        messagebox.showinfo("Checked Out", f"Check-out recorded: {now}")
        self._load_attendance()

    def _update_attendance(self):
        """
        Opens a small popup to edit the check-in and check-out
        times of the selected attendance record.
        """
        vals = self._get_selected_attendance()
        if not vals:
            return

        att_id   = vals[0]
        checkin  = vals[2]
        checkout = vals[3] if vals[3] != "--" else ""

        win = tk.Toplevel(self.root)
        win.title("Update Attendance Record")
        win.geometry("400x280")
        win.configure(bg=CARD_COLOR)
        win.resizable(False, False)
        sw = win.winfo_screenwidth()
        sh = win.winfo_screenheight()
        win.geometry(f"400x280+{(sw - 400) // 2}+{(sh - 280) // 2}")

        lbl(win, "Update Attendance Record", 13,
            bold=True, bg=CARD_COLOR).pack(
            pady=(18, 4), padx=22, anchor="w")
        tk.Frame(win, bg=ACCENT_COLOR, height=2).pack(
            fill="x", padx=22, pady=(0, 14))

        ci_field = form_row(
            win, "Check-In Time (YYYY-MM-DD HH:MM:SS)",
            value=checkin)
        co_field = form_row(
            win, "Check-Out Time (YYYY-MM-DD HH:MM:SS)",
            value=checkout)

        def save():
            new_ci = ci_field.var.get().strip()
            new_co = co_field.var.get().strip()

            if not new_ci:
                messagebox.showerror(
                    "Error", "Check-in time cannot be empty.",
                    parent=win)
                return

            conn   = self.user._db.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE attendance SET check_in=?, check_out=?"
                " WHERE id=?",
                (new_ci, new_co or None, att_id))
            conn.commit()
            conn.close()

            messagebox.showinfo(
                "Updated", "Record updated.", parent=win)
            win.destroy()
            self._load_attendance()

        btn(win, "Save Changes", save).pack(
            fill="x", padx=22, pady=6)
        btn(win, "Cancel", win.destroy,
            bg=CARD_COLOR, fg=TEXT_COLOR).pack(
            fill="x", padx=22)

    def _delete_attendance(self):
        """
        Permanently deletes the selected attendance record
        from the database after confirmation.
        """
        vals = self._get_selected_attendance()
        if not vals:
            return

        att_id = vals[0]

        if not messagebox.askyesno(
                "Delete Record",
                "Delete this attendance record? This cannot be undone."):
            return

        conn   = self.user._db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM attendance WHERE id=?", (att_id,))
        conn.commit()
        conn.close()

        self._load_attendance()

    # ── Progress section ──────────────────────────────────────

    def show_progress(self):
        """
        Shows the fitness progress tracking screen with:
          - A form to log a new weight/height/notes entry
          - BMI is auto-calculated and saved on submit
          - A table of all previous progress entries
        """
        self._clear()
        self._set_nav("My Progress")
        f = self._frame()

        header(f, "Fitness Progress",
               "Track your weight and BMI over time").pack(
            fill="x", pady=(0, 14))

        ec = card(f, padx=20, pady=14)
        ec.pack(fill="x", pady=(0, 14))
        lbl(ec, "Log New Entry", 11,
            bold=True, bg=CARD_COLOR).pack(anchor="w", pady=(0, 8))

        row = tk.Frame(ec, bg=CARD_COLOR)
        row.pack(fill="x")

        def inline_field(parent, label_text, w=10):
            lbl(parent, label_text, 9,
                color=SUBTEXT_COLOR, bg=CARD_COLOR).pack(anchor="w")
            e = tk.Entry(
                parent, font=("Arial", 11), width=w,
                bg=INPUT_BG, fg=TEXT_COLOR,
                insertbackground=TEXT_COLOR, relief="flat")
            e.pack(ipady=7, pady=(2, 0))
            return e

        wf = tk.Frame(row, bg=CARD_COLOR)
        wf.pack(side="left", padx=(0, 12))
        hf = tk.Frame(row, bg=CARD_COLOR)
        hf.pack(side="left", padx=(0, 12))
        nf = tk.Frame(row, bg=CARD_COLOR)
        nf.pack(side="left", expand=True, fill="x")

        self._wt = inline_field(wf, "Weight (kg)")
        self._ht = inline_field(hf, "Height (cm)")

        lbl(nf, "Notes", 9,
            color=SUBTEXT_COLOR, bg=CARD_COLOR).pack(anchor="w")
        self._nt = tk.Entry(
            nf, font=("Arial", 11), bg=INPUT_BG, fg=TEXT_COLOR,
            insertbackground=TEXT_COLOR, relief="flat")
        self._nt.pack(fill="x", ipady=7, pady=(2, 0))

        btn(ec, "Save Entry",
            self._save_progress).pack(anchor="w", pady=(10, 0))

        lbl(f, "Progress History", 12, bold=True).pack(
            anchor="w", pady=(8, 6))
        cols = ["Date", "Weight (kg)", "Height (cm)", "BMI", "Notes"]
        self.prog_tree, tf = make_table(f, cols, 10)
        tf.pack(fill="both", expand=True)
        self.prog_tree.column("Notes", width=240)
        self._load_progress()

    def _load_progress(self):
        """Clears and reloads the progress history table."""
        for r in self.prog_tree.get_children():
            self.prog_tree.delete(r)

        records = self.user.get_progress_records()

        if not records:
            self.prog_tree.insert(
                "", "end",
                values=("No records", "--", "--", "--", "--"))
        else:
            for r in records:
                self.prog_tree.insert("", "end", values=(
                    r["recorded_at"], r["weight_kg"],
                    r["height_cm"],   r["bmi"],
                    r["notes"] or ""))

    def _save_progress(self):
        """
        Reads weight, height and notes from the form,
        calls user.add_progress_entry() which calculates BMI
        and saves the record, then reloads the table.
        """
        w = self._wt.get().strip()
        h = self._ht.get().strip()
        n = self._nt.get().strip()

        if not w or not h:
            messagebox.showerror(
                "Error", "Weight and height required.")
            return

        try:
            bmi = self.user.add_progress_entry(float(w), float(h), n)
            messagebox.showinfo("Saved", f"Entry saved. Your BMI: {bmi}")
            self._wt.delete(0, "end")
            self._ht.delete(0, "end")
            self._nt.delete(0, "end")
            self._load_progress()
        except ValueError:
            messagebox.showerror(
                "Error", "Please enter valid numbers.")

    # ── FitBot Chat section ───────────────────────────────────

    def show_chatbot(self):
        """
        Displays the FitBot chat interface with:
          - A scrollable chat display area
          - A text input field and Send button
          - Quick-question shortcut buttons
          - A welcome message from the bot on load
        """
        self._clear()
        self._set_nav("FitBot Chat")
        f = self._frame()

        header(f, "FitBot Assistant",
               "Your personal fitness assistant").pack(
            fill="x", pady=(0, 10))

        cf = tk.Frame(f, bg=CARD_COLOR)
        cf.pack(fill="both", expand=True, pady=(0, 8))

        sb = tk.Scrollbar(cf)
        sb.pack(side="right", fill="y")

        self._chat = tk.Text(
            cf, font=("Arial", 11), bg=CARD_COLOR, fg=TEXT_COLOR,
            relief="flat", wrap="word", state="disabled",
            yscrollcommand=sb.set,
            padx=14, pady=10, spacing1=2, spacing3=4)
        self._chat.pack(fill="both", expand=True)
        sb.config(command=self._chat.yview)

        self._chat.tag_config(
            "user",
            foreground=WARNING_COLOR,
            font=("Arial", 11, "bold"))
        self._chat.tag_config(
            "bot",
            foreground="#7ec8e3",
            font=("Arial", 11))
        self._chat.tag_config(
            "lu",
            foreground=WARNING_COLOR,
            font=("Arial", 9, "bold"))
        self._chat.tag_config(
            "lb",
            foreground=ACCENT_COLOR,
            font=("Arial", 9, "bold"))

        ir = tk.Frame(f, bg=CARD_COLOR, pady=8)
        ir.pack(fill="x")

        self._inp = tk.Entry(
            ir, font=("Arial", 12), bg=INPUT_BG, fg=TEXT_COLOR,
            insertbackground=TEXT_COLOR, relief="flat")
        self._inp.pack(
            side="left", fill="x", expand=True,
            ipady=10, padx=(10, 6))
        self._inp.bind("<Return>", lambda e: self._send())

        btn(ir, "Send", self._send).pack(side="left", padx=(0, 10))

        sq = tk.Frame(f, bg=BG_COLOR)
        sq.pack(fill="x", pady=(4, 0))

        lbl(sq, "Quick questions:", 9,
            color=SUBTEXT_COLOR).pack(side="left", padx=(0, 6))

        for s in [
            "bmi 70 175",
            "Lose weight",
            "Beginner workout",
            "Diet tips",
            "Motivate me",
        ]:
            tk.Button(
                sq, text=s,
                font=("Arial", 8),
                bg=CARD_COLOR, fg=TEXT_COLOR,
                relief="flat", cursor="hand2",
                activebackground=ACCENT_COLOR,
                command=lambda m=s: self._quick(m)
            ).pack(side="left", padx=3, ipady=4, ipadx=6)

        self._append(
            "FitBot",
            # self.chatbot.get_welcome_message(),
            "bot", "lb")

    def _send(self):
        """
        Reads text from the input field, displays the user's
        message, gets a response from the Chatbot, and displays it.
        """
        txt = self._inp.get().strip()
        if not txt:
            return

        self._inp.delete(0, "end")
        self._append("You",    txt,                           "user", "lu")
        self._append("FitBot", self.chatbot.get_response(txt), "bot",  "lb")

    def _quick(self, msg):
        """
        Fills the input field with a preset question and
        immediately sends it.
        """
        self._inp.delete(0, "end")
        self._inp.insert(0, msg)
        self._send()

    def _append(self, sender, msg, tag, label_tag):
        """
        Appends a message block to the chat display.
        """
        self._chat.config(state="normal")
        self._chat.insert("end", f"\n{sender}:\n", label_tag)
        self._chat.insert("end", f"{msg}\n",        tag)
        self._chat.config(state="disabled")
        self._chat.see("end")

    # ── Logout ────────────────────────────────────────────────

    def logout(self):
        """
         Asks for confirmation then calls the logout_callback
         provided by LoginScreen. This destroys the dashboard
         Toplevel and shows the login screen again — without
         touching the root window.
         """
        if messagebox.askyesno("Logout", "Are you sure?"):
            if self.logout_callback:
               self.logout_callback()

