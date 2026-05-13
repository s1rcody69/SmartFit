# gui/components.py

import tkinter as tk
from tkinter import ttk

# ── Shared Color Palette ─────────────────────────────────────────
BG_COLOR      = "#1a1a2e"
SIDEBAR_COLOR = "#16213e"
CARD_COLOR    = "#0f3460"
ACCENT_COLOR  = "#e94560"
TEXT_COLOR    = "#eaeaea"
SUBTEXT_COLOR = "#a0a0b0"
SUCCESS_COLOR = "#2ecc71"
WARNING_COLOR = "#f39c12"
INPUT_BG      = "#1a1a2e"
BTN_COLOR     = "#e94560"
BTN_HOVER     = "#c73652"
TABLE_BG      = "#16213e"
TABLE_FG      = "#eaeaea"
TABLE_SELECT  = "#e94560"


def apply_table_style():
    """Applies a dark modern style to all ttk Treeview tables."""
    style = ttk.Style()
    style.theme_use("clam")

    style.configure("Treeview",
        background=TABLE_BG,
        foreground=TABLE_FG,
        rowheight=30,
        fieldbackground=TABLE_BG,
        borderwidth=0,
        font=("Arial", 10)
    )
    style.configure("Treeview.Heading",
        background=CARD_COLOR,
        foreground=ACCENT_COLOR,
        font=("Arial", 10, "bold"),
        borderwidth=0
    )
    style.map("Treeview",
        background=[("selected", TABLE_SELECT)],
        foreground=[("selected", "white")]
    )


class SidebarButton(tk.Button):
    """
    A reusable sidebar navigation button.

    OOP Concept - INHERITANCE:
    Inherits from tk.Button and adds our custom styling
    so we don't repeat styling code everywhere.
    """

    def __init__(self, parent, text, icon, command, **kwargs):
        super().__init__(
            parent,
            text=f"  {icon}  {text}",
            command=command,
            font=("Arial", 11),
            bg=SIDEBAR_COLOR,
            fg=TEXT_COLOR,
            activebackground=ACCENT_COLOR,
            activeforeground="white",
            relief="flat",
            anchor="w",
            cursor="hand2",
            padx=10,
            pady=12,
            **kwargs
        )
        self.default_bg = SIDEBAR_COLOR
        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_leave)

    def on_hover(self, e):
        self.config(bg=ACCENT_COLOR, fg="white")

    def on_leave(self, e):
        self.config(bg=self.default_bg, fg=TEXT_COLOR)

    def set_active(self):
        self.default_bg = ACCENT_COLOR
        self.config(bg=ACCENT_COLOR, fg="white")

    def set_inactive(self):
        self.default_bg = SIDEBAR_COLOR
        self.config(bg=SIDEBAR_COLOR, fg=TEXT_COLOR)


class StatCard(tk.Frame):
    """
    A dashboard stat card showing a number and label.
    Example: "142 Active Members"
    """

    def __init__(self, parent, title, value, icon, color=ACCENT_COLOR, **kwargs):
        super().__init__(parent, bg=CARD_COLOR, padx=20, pady=15, **kwargs)

        tk.Label(
            self, text=icon,
            font=("Arial", 24),
            bg=CARD_COLOR, fg=color
        ).pack(anchor="w")

        tk.Label(
            self, text=str(value),
            font=("Arial", 22, "bold"),
            bg=CARD_COLOR, fg=TEXT_COLOR
        ).pack(anchor="w")

        tk.Label(
            self, text=title,
            font=("Arial", 10),
            bg=CARD_COLOR, fg=SUBTEXT_COLOR
        ).pack(anchor="w")


class PageHeader(tk.Frame):
    """A consistent page title header used across all sections."""

    def __init__(self, parent, title, subtitle="", **kwargs):
        super().__init__(parent, bg=BG_COLOR, **kwargs)

        tk.Label(
            self, text=title,
            font=("Arial", 18, "bold"),
            bg=BG_COLOR, fg=TEXT_COLOR
        ).pack(anchor="w")

        if subtitle:
            tk.Label(
                self, text=subtitle,
                font=("Arial", 10),
                bg=BG_COLOR, fg=SUBTEXT_COLOR
            ).pack(anchor="w")

        # Divider line
        tk.Frame(self, bg=ACCENT_COLOR, height=2).pack(
            fill="x", pady=(8, 0)
        )


class FormField(tk.Frame):
    """A label + entry input pair used in forms."""

    def __init__(self, parent, label, show="", **kwargs):
        super().__init__(parent, bg=CARD_COLOR, **kwargs)

        tk.Label(
            self, text=label,
            font=("Arial", 9),
            bg=CARD_COLOR, fg=SUBTEXT_COLOR
        ).pack(anchor="w")

        self.var = tk.StringVar()
        self.entry = tk.Entry(
            self,
            textvariable=self.var,
            font=("Arial", 11),
            bg=INPUT_BG, fg=TEXT_COLOR,
            insertbackground=TEXT_COLOR,
            relief="flat", bd=0,
            show=show
        )
        self.entry.pack(fill="x", ipady=7, pady=(2, 8))

    def get(self):
        return self.var.get().strip()

    def set(self, value):
        self.var.set(value)

    def clear(self):
        self.var.set("")


class ActionButton(tk.Button):
    """A styled action button (Add, Edit, Delete, Search etc.)"""

    STYLES = {
        "primary": (BTN_COLOR,    BTN_HOVER,   "white"),
        "success": ("#27ae60",    "#1e8449",   "white"),
        "danger":  ("#c0392b",    "#a93226",   "white"),
        "neutral": (CARD_COLOR,   "#0a2a50",   TEXT_COLOR),
    }

    def __init__(self, parent, text, command,
                 style="primary", icon="", **kwargs):
        bg, hover, fg = self.STYLES.get(style, self.STYLES["primary"])
        label = f"{icon}  {text}" if icon else text

        super().__init__(
            parent,
            text=label,
            command=command,
            font=("Arial", 10, "bold"),
            bg=bg, fg=fg,
            activebackground=hover,
            activeforeground=fg,
            relief="flat",
            cursor="hand2",
            padx=14, pady=7,
            **kwargs
        )
        self._hover = hover
        self._bg    = bg
        self.bind("<Enter>", lambda e: self.config(bg=self._hover))
        self.bind("<Leave>", lambda e: self.config(bg=self._bg))


def make_table(parent, columns, heights=10):
    """
    Creates and returns a styled Treeview table with a scrollbar.

    Usage:
        tree, frame = make_table(parent, ["Name", "Email", "Status"])
    """
    apply_table_style()

    frame = tk.Frame(parent, bg=BG_COLOR)

    scrollbar = ttk.Scrollbar(frame, orient="vertical")
    scrollbar.pack(side="right", fill="y")

    tree = ttk.Treeview(
        frame,
        columns=columns,
        show="headings",
        height=heights,
        yscrollcommand=scrollbar.set
    )
    scrollbar.config(command=tree.yview)

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="w", width=130)

    tree.pack(fill="both", expand=True)
    return tree, frame