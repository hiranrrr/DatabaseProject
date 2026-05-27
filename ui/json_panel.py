"""
ui/json_panel.py
----------------
Sol panel bileşeni.

Sorumlulukları:
    1. JSON dosyası seçme butonu + dosya adı etiketi
    2. Yüklenen JSON'u hiyerarşik Treeview ağacında gösterme
    3. Dosya yüklendiğinde App'e haber verme (callback)
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog

from parser.json_parser import load_json
from ui.styles import (
    BG_PANEL, BG_WIDGET, ACCENT, TEXT_MAIN, TEXT_SUB,
    SUCCESS, ERROR
)


class JsonPanel(ttk.Frame):
    """
    Sol panel widget'ı.

    Parametreler:
        parent      : Üst widget (App'in content frame'i)
        on_loaded   : JSON başarıyla yüklendiğinde çağrılır
                      imza → on_loaded(data: any, filepath: str)
        on_error    : Hata durumunda çağrılır
                      imza → on_error(message: str)
    """

    def __init__(self, parent, on_loaded=None, on_error=None, **kwargs):
        super().__init__(parent, style="Panel.TFrame", **kwargs)

        self.on_loaded = on_loaded  # callback: veri yüklendiğinde App'e bildir
        self.on_error  = on_error   # callback: hata olduğunda App'e bildir

        self.json_data = None
        self.filepath  = ""

        self._build()

    # ── Arayüz kurulumu ──────────────────────────────────────────────────

    def _build(self):
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)

        # Başlık
        ttk.Label(self, text="📂  JSON Dosyası", style="Title.TLabel").grid(
            row=0, column=0, sticky="w", padx=12, pady=(12, 4)
        )

        # Buton + dosya adı satırı
        btn_row = ttk.Frame(self, style="Panel.TFrame")
        btn_row.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))

        ttk.Button(
            btn_row, text="Dosya Seç",
            style="Accent.TButton",
            command=self._browse_file
        ).pack(side="left", padx=(0, 10))

        self.file_label = ttk.Label(
            btn_row, text="Henüz dosya seçilmedi", style="Sub.TLabel"
        )
        self.file_label.pack(side="left")

        # Ağaç görünümü
        tree_frame = ttk.Frame(self, style="Panel.TFrame")
        tree_frame.grid(row=2, column=0, sticky="nsew", padx=12, pady=(0, 12))
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(tree_frame, show="tree headings")
        self.tree["columns"] = ("tip", "deger")
        self.tree.heading("#0",    text="Anahtar",  anchor="w")
        self.tree.heading("tip",   text="Tip",      anchor="w")
        self.tree.heading("deger", text="Değer",    anchor="w")
        self.tree.column("#0",    width=170, minwidth=100, stretch=True)
        self.tree.column("tip",   width=80,  minwidth=60,  stretch=False)
        self.tree.column("deger", width=180, minwidth=100, stretch=True)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical",
                             command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal",
                             command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set,
                             xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        # Tip renk etiketleri
        self.tree.tag_configure("object",    foreground="#89b4fa")  # mavi
        self.tree.tag_configure("array",     foreground="#fab387")  # turuncu
        self.tree.tag_configure("str",       foreground=TEXT_MAIN)
        self.tree.tag_configure("int",       foreground="#a6e3a1")  # yeşil
        self.tree.tag_configure("float",     foreground="#a6e3a1")
        self.tree.tag_configure("bool",      foreground="#cba6f7")  # mor
        self.tree.tag_configure("NoneType",  foreground=TEXT_SUB)

    # ── Dosya seçme ──────────────────────────────────────────────────────

    def _browse_file(self):
        path = filedialog.askopenfilename(
            title="JSON dosyası seç",
            filetypes=[("JSON Dosyaları", "*.json"), ("Tüm Dosyalar", "*.*")]
        )
        if not path:
            return

        try:
            data = load_json(path)
            self.json_data = data
            self.filepath  = path

            fname = os.path.basename(path)
            self.file_label.configure(text=fname)

            self._populate_tree(data)

            if self.on_loaded:
                self.on_loaded(data, path)

        except Exception as e:
            if self.on_error:
                self.on_error(str(e))

    # ── Ağaç doldurma ────────────────────────────────────────────────────

    def _populate_tree(self, data):
        """Treeview'i temizleyip JSON verisini hiyerarşik olarak doldurur."""
        self.tree.delete(*self.tree.get_children())
        self._insert_node(parent="", data=data, label="kök")

        # Kök düğümü aç
        roots = self.tree.get_children()
        if roots:
            self.tree.item(roots[0], open=True)

    def _insert_node(self, parent: str, data, label: str):
        """
        Özyinelemeli ağaç düğümü ekleme.
        Her veri tipine uygun renk etiketi (tag) kullanılır.
        """
        if isinstance(data, dict):
            node = self.tree.insert(
                parent, "end",
                text=f"  {label}",
                values=("object", f"{{{len(data)} alan}}"),
                tags=("object",)
            )
            for k, v in data.items():
                self._insert_node(node, v, k)

        elif isinstance(data, list):
            node = self.tree.insert(
                parent, "end",
                text=f"  {label}",
                values=("array", f"[{len(data)} eleman]"),
                tags=("array",)
            )
            for i, item in enumerate(data[:50]):   # max 50 eleman göster
                self._insert_node(node, item, f"[{i}]")
            if len(data) > 50:
                self.tree.insert(node, "end",
                                 text="  ...",
                                 values=("", f"{len(data)-50} eleman daha"))

        else:
            type_name = type(data).__name__
            display   = str(data)
            if len(display) > 80:
                display = display[:77] + "..."

            self.tree.insert(
                parent, "end",
                text=f"  {label}",
                values=(type_name, display),
                tags=(type_name,)
            )

    # ── Public API ───────────────────────────────────────────────────────

    def clear(self):
        """Paneli sıfırlar (Sıfırla butonunda çağrılır)."""
        self.json_data = None
        self.filepath  = ""
        self.file_label.configure(text="Henüz dosya seçilmedi")
        self.tree.delete(*self.tree.get_children())

    def get_data(self):
        """Yüklenmiş JSON verisini döndürür."""
        return self.json_data

    def get_filepath(self):
        """Yüklenmiş dosyanın yolunu döndürür."""
        return self.filepath