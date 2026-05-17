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

        for i, (title, val, color) in enumerate([
            ("My Plan",
             getattr(self.user, "membership_plan", "Basic"),
             WARNING_COLOR),
            ("Status",
             getattr(self.user, "status", "Active"),
             SUCCESS_COLOR),
            ("Expires",
             getattr(self.user, "membership_end", "N/A") or "N/A",
             "#9b59b6"),
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

        btn(c, "Save Changes",
            self._save_profile).pack(anchor="w", pady=(14, 0))

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

    # ── Membership section ────────────────────────────────────

    def show_membership(self):
        """
        Shows the member's current membership details:
          - Plan name (highlighted badge)
          - Status, start date, expiry date
          - Days remaining (colour-coded: green/orange/red)
          - Upgrade instructions
        """
        self._clear()
        self._set_nav("Membership")
        f = self._frame()

        header(f, "My Membership",
               "Current plan and membership details").pack(
            fill="x", pady=(0, 18))

        c = card(f, padx=28, pady=22)
        c.pack(fill="x")

        plan   = getattr(self.user, "membership_plan",  "Basic")
        start  = getattr(self.user, "membership_start", "N/A")
        end    = getattr(self.user, "membership_end",   "N/A")
        status = getattr(self.user, "status",           "Active")

        # Plan badge
        badge = tk.Frame(c, bg=ACCENT_COLOR, padx=14, pady=8)
        badge.pack(anchor="w", pady=(0, 14))
        lbl(badge, f"{plan} Plan", 13,
            bold=True, bg=ACCENT_COLOR, color="white").pack()

        # Detail rows
        for label, val in [
            ("Status",     status),
            ("Start Date", start),
            ("Expiry",     end or "N/A"),
        ]:
            row = tk.Frame(c, bg=CARD_COLOR)
            row.pack(fill="x", pady=3)
            lbl(row, f"{label}:", 10, bold=True,
                color=SUBTEXT_COLOR, bg=CARD_COLOR,
                width=12, anchor="w").pack(side="left")
            lbl(row, val or "N/A", 10,
                bg=CARD_COLOR).pack(side="left")

        # Days remaining countdown — colour-coded
        if end and end != "N/A":
            try:
                days  = (date.fromisoformat(end) - date.today()).days
                color = (
                    "#2ecc71"    if days > 7
                    else WARNING_COLOR if days >= 0
                    else ACCENT_COLOR
                )
                text = (
                    f"Expired {abs(days)} days ago"
                    if days < 0
                    else f"{days} days remaining"
                )
                tk.Frame(c, bg=INPUT_BG, height=1).pack(
                    fill="x", pady=10)
                lbl(c, text, 13, bold=True,
                    color=color, bg=CARD_COLOR).pack(anchor="w")
            except Exception:
                pass

        tk.Frame(c, bg=INPUT_BG, height=1).pack(fill="x", pady=10)
        lbl(c,
            "To upgrade or renew, contact the front desk or admin.",
            9, color=SUBTEXT_COLOR, bg=CARD_COLOR).pack(anchor="w")

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
            # No plan assigned — show empty state
            c = card(f, padx=28, pady=28)
            c.pack(fill="x")
            lbl(c, "No workout plan assigned yet", 13,
                bold=True, bg=CARD_COLOR).pack(pady=(8, 4))
            lbl(c, "Ask your trainer or admin to assign a plan.", 10,
                color=SUBTEXT_COLOR, bg=CARD_COLOR).pack()
            btn(c, "Ask FitBot for Ideas",
                self.show_chatbot).pack(pady=(14, 0))
            return

        # Display the assigned plan
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

        # Read-only text area showing the exercise description
        t = tk.Text(
            c, font=("Arial", 11), bg=INPUT_BG, fg=TEXT_COLOR,
            relief="flat", wrap="word", height=12)
        t.pack(fill="both", expand=True, pady=(8, 0))
        t.insert("1.0", plan.get("exercises", "No details provided."))
        t.config(state="disabled")   # prevent editing

    # ── Attendance section ────────────────────────────────────

    def show_attendance(self):
        """
        Shows the member's last 30 check-in records in a table,
        plus a check-in button at the top.
        """
        self._clear()
        self._set_nav("Attendance")
        f = self._frame()

        header(f, "Attendance History",
               "Your last 30 gym visits").pack(
            fill="x", pady=(0, 14))

        btn(f, "Check In Now",
            self._do_checkin, bg="#27ae60").pack(
            anchor="w", pady=(0, 10))

        cols  = ["#", "Check-In Time", "Check-Out Time"]
        tree, tf = make_table(f, cols, 16)
        tf.pack(fill="both", expand=True)

        records = self.user.get_attendance_history()

        if not records:
            tree.insert("", "end",
                        values=("--", "No records yet", "--"))
        else:
            for i, r in enumerate(records, 1):
                tree.insert("", "end", values=(
                    i,
                    r["check_in"],
                    r["check_out"] or "--"))

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

        # Entry form card
        ec = card(f, padx=20, pady=14)
        ec.pack(fill="x", pady=(0, 14))
        lbl(ec, "Log New Entry", 11,
            bold=True, bg=CARD_COLOR).pack(anchor="w", pady=(0, 8))

        row = tk.Frame(ec, bg=CARD_COLOR)
        row.pack(fill="x")

        def inline_field(parent, label_text, w=10):
            """
            Helper that creates a label + entry inline
            (no form_row used here so entries sit side by side).
            """
            lbl(parent, label_text, 9,
                color=SUBTEXT_COLOR, bg=CARD_COLOR).pack(anchor="w")
            e = tk.Entry(
                parent, font=("Arial", 11), width=w,
                bg=INPUT_BG, fg=TEXT_COLOR,
                insertbackground=TEXT_COLOR, relief="flat")
            e.pack(ipady=7, pady=(2, 0))
            return e

        # Three columns: Weight | Height | Notes
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

        # History table
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
            # Clear the input fields after saving
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

        Messages are colour-coded:
          User messages  — orange/yellow
          FitBot replies — light blue
        """
        self._clear()
        self._set_nav("FitBot Chat")
        f = self._frame()

        header(f, "FitBot Assistant",
               "Your personal fitness assistant").pack(
            fill="x", pady=(0, 10))

        # Chat display area — disabled Text widget (read-only)
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

        # Text tags to style user vs bot messages differently
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

        # Input row — entry + send button side by side
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

        # Quick-question buttons — pre-filled shortcuts
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

        # Show the bot welcome message on load
        self._append(
            "FitBot",
            self.chatbot.get_welcome_message(),
            "bot", "lb")

    def _send(self):
        """
        Reads text from the input field, displays the user's
        message, gets a response from the Chatbot, and displays it.
        Clears the input field after sending.
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
        immediately sends it (simulates the user typing it).
        """
        self._inp.delete(0, "end")
        self._inp.insert(0, msg)
        self._send()

    def _append(self, sender, msg, tag, label_tag):
        """
        Appends a message block to the chat display.
        The display is temporarily enabled for writing,
        then locked again to prevent user editing.
        Auto-scrolls to the latest message.

        Parameters:
            sender    — display name ("You" or "FitBot")
            msg       — the message text
            tag       — text colour tag ("user" or "bot")
            label_tag — sender name colour tag ("lu" or "lb")
        """
        self._chat.config(state="normal")
        self._chat.insert("end", f"\n{sender}:\n", label_tag)
        self._chat.insert("end", f"{msg}\n",        tag)
        self._chat.config(state="disabled")
        self._chat.see("end")   # scroll to bottom

    # ── Logout ────────────────────────────────────────────────

    def logout(self):
        """
        Asks for confirmation, destroys the dashboard window,
        and relaunches a fresh login screen.
        """
        if messagebox.askyesno("Logout", "Are you sure?"):
            self.root.destroy()
            import tkinter as tk2
            from gui.login_screen import LoginScreen
            r = tk2.Tk()
            LoginScreen(r)
            r.mainloop()
