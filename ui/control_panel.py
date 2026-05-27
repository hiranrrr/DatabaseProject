"""
ui/control_panel.py
-------------------
Orta panel bileşeni.

Sorumlulukları:
    1. "Dönüştür" butonu  → App'e dönüşüm komutu gönderir
    2. "Sıfırla"  butonu  → App'e sıfırlama komutu gönderir
    3. Log alanı          → App'ten gelen mesajları renkli gösterir
"""

import tkinter as tk
from tkinter import ttk

from ui.styles import (
    BG_PANEL, BG_WIDGET,
    TEXT_MAIN, TEXT_SUB,
    SUCCESS, ERROR, WARNING, ACCENT
)


class ControlPanel(ttk.Frame):
    """
    Orta panel widget'ı.

    Parametreler:
        parent      : Üst widget
        on_convert  : "Dönüştür" butonuna basıldığında çağrılır
        on_reset    : "Sıfırla"  butonuna basıldığında çağrılır
    """

    def __init__(self, parent, on_convert=None, on_reset=None, **kwargs):
        super().__init__(parent, style="Panel.TFrame", **kwargs)

        self.on_convert = on_convert
        self.on_reset   = on_reset

        self._build()

    # ── Arayüz kurulumu ──────────────────────────────────────────────────

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

        # Ayırıcı çizgi
        sep = tk.Frame(self, bg=ACCENT, height=1)
        sep.grid(row=3, column=0, sticky="ew", padx=12, pady=(0, 8))

        # Log başlığı
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

        # Renk etiketlerini tanımla
        self.log_box.tag_configure("success", foreground=SUCCESS)
        self.log_box.tag_configure("error",   foreground=ERROR)
        self.log_box.tag_configure("warning", foreground=WARNING)
        self.log_box.tag_configure("info",    foreground=TEXT_SUB)

    # ── Buton handler'ları ───────────────────────────────────────────────

    def _on_convert_click(self):
        if self.on_convert:
            self.on_convert()

    def _on_reset_click(self):
        if self.on_reset:
            self.on_reset()

    # ── Public API ───────────────────────────────────────────────────────

    def log(self, message: str, level: str = "info"):
        """
        Log alanına renkli mesaj ekler.

        Parametreler:
            message : Gösterilecek metin
            level   : "info" | "success" | "error" | "warning"

        Kullanım (App içinden):
            self.control_panel.log("Dönüşüm tamamlandı", "success")
        """
        self.log_box.configure(state="normal")
        self.log_box.insert("end", message + "\n", level)
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def clear_log(self):
        """Log alanını temizler."""
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")