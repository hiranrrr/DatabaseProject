import os
import tkinter as tk
from tkinter import ttk, filedialog

from parser.json_parser import load_json
from ui.styles import (
    BG_PANEL, BG_WIDGET, ACCENT, TEXT_MAIN, TEXT_SUB,
    SUCCESS, ERROR
)


class JsonPanel(tk.Frame):

    def __init__(self, parent, on_loaded=None, on_error=None, **kwargs):
        super().__init__(parent, bg=BG_PANEL, **kwargs)

        self.on_loaded = on_loaded
        self.on_error  = on_error
        self.json_data = None
        self.filepath  = ""

        self._build()

    def _build(self):
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)

        tk.Label(
            self, text="📂  JSON Dosyası",
            bg=BG_PANEL, fg=TEXT_MAIN,
            font=("Segoe UI", 11, "bold")
        ).grid(row=0, column=0, sticky="w", padx=12, pady=(12, 4))

        # Buton + dosya adı satırı
        btn_row = tk.Frame(self, bg=BG_PANEL)
        btn_row.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))

        ttk.Button(
            btn_row, text="Dosya Seç",
            style="Accent.TButton",
            command=self._browse_file
        ).pack(side="left", padx=(0, 10))

        self.file_label = tk.Label(
            btn_row, text="Henüz dosya seçilmedi",
            bg=BG_PANEL, fg=TEXT_SUB,
            font=("Segoe UI", 9)
        )
        self.file_label.pack(side="left")

        # Ağaç görünümü
        tree_frame = tk.Frame(self, bg=BG_PANEL)
        tree_frame.grid(row=2, column=0, sticky="nsew", padx=12, pady=(0, 12))
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.rowconfigure(1, weight=0)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.columnconfigure(1, weight=0)

        self.tree = ttk.Treeview(tree_frame, show="tree")
        self.tree["columns"] = ()
        self.tree.column("#0", width=300, minwidth=200, stretch=True)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical",
                             command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal",
                             command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set,
                             xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        self.tree.tag_configure("object",   foreground="#89b4fa")
        self.tree.tag_configure("array",    foreground="#fab387")
        self.tree.tag_configure("str",      foreground=TEXT_MAIN)
        self.tree.tag_configure("int",      foreground="#a6e3a1")
        self.tree.tag_configure("float",    foreground="#a6e3a1")
        self.tree.tag_configure("bool",     foreground="#cba6f7")
        self.tree.tag_configure("NoneType", foreground=TEXT_SUB)

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

    def _populate_tree(self, data):
        self.tree.delete(*self.tree.get_children())
        self._insert_node(parent="", data=data, label="kök", depth=0)
        # Kök ve ilk seviye düğümleri aç
        roots = self.tree.get_children()
        if roots:
            self.tree.item(roots[0], open=True)
            for child in self.tree.get_children(roots[0]):
                self.tree.item(child, open=True)

    def _insert_node(self, parent: str, data, label: str, depth: int = 0):
        if isinstance(data, dict):
            node = self.tree.insert(
                parent, "end",
                text=f"  {label}  •  object  ({len(data)} alan)",
                tags=("object",),
                open=(depth < 2)   # ilk 2 seviye otomatik açık
            )
            for k, v in data.items():
                self._insert_node(node, v, k, depth + 1)

        elif isinstance(data, list):
            node = self.tree.insert(
                parent, "end",
                text=f"  {label}  •  array  [{len(data)} eleman]",
                tags=("array",),
                open=(depth < 1)   # kök array açık, diğerleri kapalı
            )
            for i, item in enumerate(data[:50]):
                self._insert_node(node, item, f"[{i}]", depth + 1)
            if len(data) > 50:
                self.tree.insert(node, "end",
                                 text=f"  ... {len(data)-50} eleman daha")
        else:
            type_name = type(data).__name__
            display   = str(data)
            if len(display) > 60:
                display = display[:57] + "..."
            self.tree.insert(
                parent, "end",
                text=f"  {label}: {display}  ({type_name})",
                tags=(type_name,)
            )

    def clear(self):
        self.json_data = None
        self.filepath  = ""
        self.file_label.configure(text="Henüz dosya seçilmedi")
        self.tree.delete(*self.tree.get_children())

    def get_data(self):
        return self.json_data

    def get_filepath(self):
        return self.filepath