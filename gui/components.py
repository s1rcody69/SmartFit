
# =============================================================
# Shared UI building blocks used across all dashboard screens.
# Instead of repeating the same widget code everywhere, we
# define reusable factories here and import them where needed.
# This follows the DRY principle (Don't Repeat Yourself).
# =============================================================

import tkinter as tk
from tkinter import ttk

# ------------------------------------------------------------------
# Colour palette — defined once here so every screen stays
# consistent. Change a colour here and it updates everywhere.
# ------------------------------------------------------------------
BG_COLOR      = "#1a1a2e"   # Main window background (dark navy)
SIDEBAR_COLOR = "#16213e"   # Sidebar panel background
CARD_COLOR    = "#0f3460"   # Card / popup background
ACCENT_COLOR  = "#e94560"   # Primary accent (red)
TEXT_COLOR    = "#eaeaea"   # Main text colour (light grey)
SUBTEXT_COLOR = "#a0a0b0"   # Secondary / label text
SUCCESS_COLOR = "#2ecc71"   # Green — used for active status
WARNING_COLOR = "#f39c12"   # Orange — used for warnings
INPUT_BG      = "#1a1a2e"   # Entry field background
BTN_COLOR     = "#e94560"   # Default button colour
BTN_HOVER     = "#c73652"   # Button hover colour
TABLE_BG      = "#16213e"   # Table row background
TABLE_SELECT  = "#e94560"   # Selected row highlight


def apply_table_style():
    """
    Applies a consistent dark theme to all ttk Treeview tables.
    Called automatically inside make_table() so you never need
    to call it directly.
    """
    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        "Treeview",
        background=TABLE_BG,
        foreground=TEXT_COLOR,
        rowheight=30,
        fieldbackground=TABLE_BG,
        font=("Arial", 10)
    )
    style.configure(
        "Treeview.Heading",
        background=CARD_COLOR,
        foreground=ACCENT_COLOR,
        font=("Arial", 10, "bold")
    )
    style.map(
        "Treeview",
        background=[("selected", TABLE_SELECT)],
        foreground=[("selected", "white")]
    )


def make_table(parent, columns, heights=10):
    """
    Creates a styled Treeview table with a vertical scrollbar.

    Parameters:
        parent  — the frame to place the table in
        columns — list of column header strings
        heights — number of visible rows (default 10)

    Returns:
        tree  — the Treeview widget (use tree.insert() to add rows)
        frame — the container Frame (pack/grid this into the layout)

    Usage:
        tree, frame = make_table(parent, ["Name", "Email"], heights=12)
        frame.pack(fill="both", expand=True)
        tree.insert("", "end", values=("John", "john@email.com"))
    """
    apply_table_style()

    frame = tk.Frame(parent, bg=BG_COLOR)

    # Scrollbar on the right side
    scrollbar = ttk.Scrollbar(frame, orient="vertical")
    scrollbar.pack(side="right", fill="y")

    tree = ttk.Treeview(
        frame,
        columns=columns,
        show="headings",       # hide the default empty first column
        height=heights,
        yscrollcommand=scrollbar.set
    )
    scrollbar.config(command=tree.yview)

    # Set heading labels and default column widths
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="w", width=130)

    tree.pack(fill="both", expand=True)
    return tree, frame


def lbl(parent, text, font_size=10, bold=False,
        color=TEXT_COLOR, bg=BG_COLOR, **kw):
    """
    Creates and returns a styled tk.Label.
    A shorthand so we don't repeat font/colour args everywhere.

    Parameters:
        parent    — parent widget
        text      — label text
        font_size — font size (default 10)
        bold      — True for bold font weight
        color     — foreground (text) colour
        bg        — background colour
        **kw      — any extra tk.Label keyword arguments
    """
    weight = "bold" if bold else "normal"
    return tk.Label(
        parent,
        text=text,
        font=("Arial", font_size, weight),
        bg=bg,
        fg=color,
        **kw
    )


def entry(parent, var=None, show="", width=None):
    """
    Creates and returns a styled tk.Entry input field.
    Attaches the StringVar as entry.var so callers can do
    entry.var.get() to read the value.

    Parameters:
        parent — parent widget
        var    — optional existing StringVar (creates one if None)
        show   — character to mask input e.g. "*" for passwords
        width  — optional fixed character width
    """
    if var is None:
        var = tk.StringVar()

    kw = dict(
        textvariable=var,
        font=("Arial", 11),
        bg=INPUT_BG,
        fg=TEXT_COLOR,
        insertbackground=TEXT_COLOR,   # cursor colour
        relief="flat",
        bd=0
    )
    if width:
        kw["width"] = width

    e = tk.Entry(parent, **kw, show=show)
    e.var = var   # attach var so callers can do: field.var.get()
    return e


def btn(parent, text, command, bg=BTN_COLOR, fg="white", **kw):
    """
    Creates and returns a styled tk.Button with hover effect.
    The hover colour is looked up from a map based on bg colour.

    Parameters:
        parent  — parent widget
        text    — button label
        command — function to call when clicked
        bg      — background colour (controls hover colour too)
        fg      — foreground (text) colour
        **kw    — any extra tk.Button keyword arguments
    """
    # Map each base colour to its darker hover version
    hover_map = {
        BTN_COLOR:  BTN_HOVER,
        "#27ae60":  "#1e8449",   # green  -> darker green
        "#c0392b":  "#a93226",   # red    -> darker red
        CARD_COLOR: "#0a2a50",   # card   -> darker card
    }
    hover = hover_map.get(bg, bg)

    b = tk.Button(
        parent,
        text=text,
        command=command,
        font=("Arial", 10, "bold"),
        bg=bg,
        fg=fg,
        activebackground=hover,
        activeforeground=fg,
        relief="flat",
        cursor="hand2",
        padx=14,
        pady=7,
        **kw
    )
    # Bind hover colour change on mouse enter / leave
    b.bind("<Enter>", lambda e: b.config(bg=hover))
    b.bind("<Leave>", lambda e: b.config(bg=bg))
    return b


def header(parent, title, subtitle=""):
    """
    Creates a page header block: large title, optional subtitle,
    and a red accent underline.
    Used at the top of every dashboard section.

    Parameters:
        parent   — parent widget
        title    — main heading text
        subtitle — smaller text shown below the title (optional)

    Returns the containing Frame (caller must pack/grid it).
    """
    frame = tk.Frame(parent, bg=BG_COLOR)

    lbl(frame, title, 18, bold=True).pack(anchor="w")

    if subtitle:
        lbl(frame, subtitle, 10, color=SUBTEXT_COLOR).pack(anchor="w")

    # Red accent divider line
    tk.Frame(frame, bg=ACCENT_COLOR, height=2).pack(
        fill="x", pady=(6, 0)
    )
    return frame


def card(parent, padx=20, pady=14):
    """
    Returns a styled dark card Frame.
    Used to group related content visually on a screen.
    """
    return tk.Frame(parent, bg=CARD_COLOR, padx=padx, pady=pady)


def form_row(parent, label_text, show="", value=""):
    """
    Creates a label + entry pair stacked vertically.
    Used inside forms and popup windows for each input field.

    Parameters:
        parent     — parent widget (usually a popup or card frame)
        label_text — the field label shown above the entry
        show       — mask character for password fields (e.g. "*")
        value      — pre-filled default value

    Returns the entry widget (with .var attached).
    """
    lbl(parent, label_text, 9,
        color=SUBTEXT_COLOR, bg=CARD_COLOR).pack(anchor="w")

    var = tk.StringVar(value=value)
    e = entry(parent, var=var, show=show)
    e.pack(fill="x", ipady=7, pady=(2, 10))
    return e


def popup(root, title, w=440, h=400):
    """
    Creates and returns a centered Toplevel popup window.
    All popup forms (Add Member, Edit Trainer, etc.) use this
    so they all appear in the centre of the screen consistently.

    Parameters:
        root  — the main application window (for centering)
        title — window title bar text
        w, h  — width and height in pixels
    """
    win = tk.Toplevel(root)
    win.title(title)
    win.configure(bg=CARD_COLOR)
    win.resizable(False, False)

    # Calculate centre position
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    win.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")
    return win


def popup_header(win, title):
    """
    Adds a bold title and red divider to a popup window.
    Called right after popup() to give every form a consistent header.
    """
    lbl(win, title, 14, bold=True,
        bg=CARD_COLOR).pack(pady=(18, 4), padx=22, anchor="w")
    tk.Frame(win, bg=ACCENT_COLOR, height=2).pack(
        fill="x", padx=22, pady=(0, 14)
    )


def dropdown(parent, values, default=None):
    """
    Creates a styled read-only Combobox (dropdown menu).

    Parameters:
        parent  — parent widget
        values  — list of option strings
        default — pre-selected value (defaults to first item)

    Returns:
        combobox widget, StringVar
    Usage:
        cb, var = dropdown(parent, ["Cash", "M-Pesa"])
        selected = var.get()
    """
    var = tk.StringVar(value=default or (values[0] if values else ""))
    cb = ttk.Combobox(
        parent,
        textvariable=var,
        values=values,
        state="readonly",
        font=("Arial", 11)
    )
    return cb, var


class SidebarButton(tk.Button):
    """
    A navigation button used in the sidebar.

    OOP Concept - INHERITANCE:
    Inherits from tk.Button and extends it with:
      - Consistent dark sidebar styling applied automatically
      - Hover highlight effect on mouse enter / leave
      - set_active() / set_inactive() to show the current page

    Usage:
        b = SidebarButton(sidebar, "Members", command)
        b.pack(fill="x")
        b.set_active()    # highlight this button
        b.set_inactive()  # return to normal style
    """

    def __init__(self, parent, text, command, **kw):
        # Call the parent tk.Button constructor with our default styling
        super().__init__(
            parent,
            text=f"  {text}",      # indent text for visual padding
            command=command,
            font=("Arial", 11),
            bg=SIDEBAR_COLOR,
            fg=TEXT_COLOR,
            activebackground=ACCENT_COLOR,
            activeforeground="white",
            relief="flat",
            anchor="w",            # left-align text
            cursor="hand2",
            padx=10,
            pady=12,
            **kw
        )
        # Store the default bg so we can restore it on mouse leave
        self._default_bg = SIDEBAR_COLOR

        self.bind("<Enter>",
                  lambda e: self.config(bg=ACCENT_COLOR, fg="white"))
        self.bind("<Leave>",
                  lambda e: self.config(
                      bg=self._default_bg, fg=TEXT_COLOR))

    def set_active(self):
        """Highlights this button to show it is the current page."""
        self._default_bg = ACCENT_COLOR
        self.config(bg=ACCENT_COLOR, fg="white")

    def set_inactive(self):
        """Returns this button to its default unselected style."""
        self._default_bg = SIDEBAR_COLOR
        self.config(bg=SIDEBAR_COLOR, fg=TEXT_COLOR)