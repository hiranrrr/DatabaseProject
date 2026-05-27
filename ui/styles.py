"""
styles.py
---------
Uygulamadaki tüm renk sabitleri ve ttk stil tanımları bu dosyada tutulur.
Herhangi bir rengi değiştirmek istersen sadece buraya bakman yeterli.
"""

import tkinter as tk
from tkinter import ttk

# ── Renk Paleti ──────────────────────────────────────────────────────────────
BG_DARK   = "#1e1e2e"
BG_PANEL  = "#2a2a3e"
BG_WIDGET = "#313145"
ACCENT    = "#7c6af7"
ACCENT_H  = "#9b8df9"
TEXT_MAIN = "#cdd6f4"
TEXT_SUB  = "#a6adc8"
SUCCESS   = "#a6e3a1"
ERROR     = "#f38ba8"
WARNING   = "#f9e2af"
BORDER    = "#45475a"


def apply(root: tk.Tk):
    """
    ttk stillerini uygulamaya uygular.
    main.py içinde App.__init__ tarafından bir kez çağrılır.
    """
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure("TFrame",       background=BG_DARK)
    style.configure("Panel.TFrame", background=BG_PANEL)

    style.configure("TLabel",
                    background=BG_PANEL, foreground=TEXT_MAIN,
                    font=("Segoe UI", 10))
    style.configure("Title.TLabel",
                    background=BG_PANEL, foreground=TEXT_MAIN,
                    font=("Segoe UI", 11, "bold"))
    style.configure("Sub.TLabel",
                    background=BG_PANEL, foreground=TEXT_SUB,
                    font=("Segoe UI", 9))

    style.configure("Accent.TButton",
                    background=ACCENT, foreground="#ffffff",
                    font=("Segoe UI", 10, "bold"),
                    borderwidth=0, focusthickness=0)
    style.map("Accent.TButton",
              background=[("active", ACCENT_H)])

    style.configure("Danger.TButton",
                    background="#e06c75", foreground="#ffffff",
                    font=("Segoe UI", 10), borderwidth=0)
    style.map("Danger.TButton",
              background=[("active", ERROR)])

    style.configure("Treeview",
                    background=BG_WIDGET, foreground=TEXT_MAIN,
                    fieldbackground=BG_WIDGET, rowheight=24,
                    font=("Consolas", 9))
    style.configure("Treeview.Heading",
                    background=BG_PANEL, foreground=ACCENT,
                    font=("Segoe UI", 9, "bold"))
    style.map("Treeview",
              background=[("selected", ACCENT)])

    style.configure("TCombobox",
                    fieldbackground=BG_WIDGET, background=BG_WIDGET,
                    foreground=TEXT_MAIN, selectbackground=ACCENT)

    style.configure("TScrollbar",
                    background=BG_PANEL, troughcolor=BG_WIDGET,
                    borderwidth=0, arrowsize=12)