import tkinter as tk
from tkinter import ttk

from ui.styles import (
    BG_PANEL, BG_WIDGET,
    TEXT_MAIN, TEXT_SUB,
    SUCCESS, ERROR, WARNING, ACCENT
)


class ControlPanel(ttk.Frame):
 
    def __init__(self, parent, on_convert=None, on_reset=None, **kwargs):
        super().__init__(parent, style="Panel.TFrame", **kwargs)

        self.on_convert = on_convert #donustur butonu
        self.on_reset   = on_reset #sıfırlama tusu

        self._build()

    def _build(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(4, weight=1)   # log alanı genişlesin

        # Başlık
        ttk.Label(self, text="⚙️  İşlemler", style="Title.TLabel").grid(
            row=0, column=0, sticky="w", padx=12, pady=(12, 16)
        )

        # Dönüştür butonu
        ttk.Button(
            self, text="🔄  Dönüştür",
            style="Accent.TButton",
            command=self._on_convert_click
        ).grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))

        # Sıfırla butonu
        ttk.Button(
            self, text="🗑️  Sıfırla",
            style="Danger.TButton",
            command=self._on_reset_click
        ).grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 20))

        sep = tk.Frame(self, bg=ACCENT, height=1)
        sep.grid(row=3, column=0, sticky="ew", padx=12, pady=(0, 8))

        ttk.Label(self, text="İşlem Günlüğü", style="Sub.TLabel").grid(
            row=4, column=0, sticky="w", padx=12
        )

        # Log metin alanı
        log_frame = ttk.Frame(self, style="Panel.TFrame")
        log_frame.grid(row=5, column=0, sticky="nsew", padx=12, pady=(4, 12))
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        self.rowconfigure(5, weight=1)

        self.log_box = tk.Text(
            log_frame,
            bg=BG_WIDGET, fg=TEXT_MAIN,
            font=("Consolas", 8),
            wrap="word",
            state="disabled",
            relief="flat",
            insertbackground=TEXT_MAIN,
            cursor="arrow"
        )
        log_vsb = ttk.Scrollbar(log_frame, orient="vertical",
                                 command=self.log_box.yview)
        self.log_box.configure(yscrollcommand=log_vsb.set)

        self.log_box.grid(row=0, column=0, sticky="nsew")
        log_vsb.grid(row=0, column=1, sticky="ns")

        self.log_box.tag_configure("success", foreground=SUCCESS)
        self.log_box.tag_configure("error",   foreground=ERROR)
        self.log_box.tag_configure("warning", foreground=WARNING)
        self.log_box.tag_configure("info",    foreground=TEXT_SUB)

    

    def _on_convert_click(self): #donusture tıklama
        if self.on_convert: #silmeye tıklama
            self.on_convert()

    def _on_reset_click(self):
        if self.on_reset:
            self.on_reset()

    #islemleri loglar
    def log(self, message: str, level: str = "info"):
        
        self.log_box.configure(state="normal")
        self.log_box.insert("end", message + "\n", level)
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def clear_log(self): #logu temizler
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")