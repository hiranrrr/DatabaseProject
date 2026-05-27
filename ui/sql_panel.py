"""
ui/sql_panel.py
---------------
Sağ panel bileşeni.

Sorumlulukları:
    1. Oluşturulan SQL tablolarını Combobox ile listeler
    2. Seçilen tablonun içeriğini DataGrid (Treeview) ile gösterir
    3. Seçilen tablonun CREATE TABLE SQL'ini ayrı sekmede gösterir
    4. Tablo istatistiklerini (satır sayısı, sütun sayısı) gösterir
"""

import tkinter as tk
from tkinter import ttk

from ui.styles import (
    BG_PANEL, BG_WIDGET,
    ACCENT, TEXT_MAIN, TEXT_SUB, SUCCESS
)


class SqlPanel(ttk.Frame):
    """
    Sağ panel widget'ı.

    Parametreler:
        parent          : Üst widget
        on_table_select : Tablo seçildiğinde çağrılır
                          imza → on_table_select(table_name: str)
    """

    def __init__(self, parent, on_table_select=None, **kwargs):
        super().__init__(parent, style="Panel.TFrame", **kwargs)

        self.on_table_select = on_table_select

        self._build()

    # ── Arayüz kurulumu ──────────────────────────────────────────────────

    def _build(self):
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)

        # Başlık
        ttk.Label(self, text="🗃️  SQL Tabloları", style="Title.TLabel").grid(
            row=0, column=0, sticky="w", padx=12, pady=(12, 4)
        )

        # Tablo seçici satırı
        sel_row = ttk.Frame(self, style="Panel.TFrame")
        sel_row.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))

        ttk.Label(sel_row, text="Tablo:", style="TLabel").pack(side="left")

        self.table_var = tk.StringVar()
        self.table_combo = ttk.Combobox(
            sel_row,
            textvariable=self.table_var,
            state="readonly",
            width=22
        )
        self.table_combo.pack(side="left", padx=(8, 12))
        self.table_combo.bind("<<ComboboxSelected>>", self._on_table_selected)

        # İstatistik etiketi (satır/sütun sayısı)
        self.stat_label = ttk.Label(sel_row, text="", style="Sub.TLabel")
        self.stat_label.pack(side="left")

        # Notebook: Veri & Şema sekmeleri
        notebook = ttk.Notebook(self)
        notebook.grid(row=2, column=0, sticky="nsew", padx=12, pady=(0, 12))

        # ── Sekme 1: Veri ────────────────────────────────────────────────
        data_tab = ttk.Frame(notebook, style="Panel.TFrame")
        data_tab.rowconfigure(0, weight=1)
        data_tab.columnconfigure(0, weight=1)
        notebook.add(data_tab, text="  📄 Veri  ")

        self.data_grid = ttk.Treeview(data_tab, show="headings")
        grid_vsb = ttk.Scrollbar(data_tab, orient="vertical",
                                  command=self.data_grid.yview)
        grid_hsb = ttk.Scrollbar(data_tab, orient="horizontal",
                                  command=self.data_grid.xview)
        self.data_grid.configure(yscrollcommand=grid_vsb.set,
                                  xscrollcommand=grid_hsb.set)

        self.data_grid.grid(row=0, column=0, sticky="nsew")
        grid_vsb.grid(row=0, column=1, sticky="ns")
        grid_hsb.grid(row=1, column=0, sticky="ew")

        # Zebra çizgileri
        self.data_grid.tag_configure("odd",  background=BG_WIDGET)
        self.data_grid.tag_configure("even", background="#38384e")

        # ── Sekme 2: SQL Şeması ──────────────────────────────────────────
        schema_tab = ttk.Frame(notebook, style="Panel.TFrame")
        schema_tab.rowconfigure(0, weight=1)
        schema_tab.columnconfigure(0, weight=1)
        notebook.add(schema_tab, text="  🔧 SQL Şeması  ")

        self.schema_box = tk.Text(
            schema_tab,
            bg=BG_WIDGET, fg="#89dceb",       # cyan — SQL rengi
            font=("Consolas", 9),
            wrap="none",
            state="disabled",
            relief="flat",
            insertbackground=TEXT_MAIN
        )
        schema_vsb = ttk.Scrollbar(schema_tab, orient="vertical",
                                    command=self.schema_box.yview)
        schema_hsb = ttk.Scrollbar(schema_tab, orient="horizontal",
                                    command=self.schema_box.xview)
        self.schema_box.configure(yscrollcommand=schema_vsb.set,
                                   xscrollcommand=schema_hsb.set)

        self.schema_box.grid(row=0, column=0, sticky="nsew")
        schema_vsb.grid(row=0, column=1, sticky="ns")
        schema_hsb.grid(row=1, column=0, sticky="ew")

        # SQL syntax renklendirme etiketleri
        self.schema_box.tag_configure("keyword",  foreground="#cba6f7")  # mor
        self.schema_box.tag_configure("type",     foreground="#fab387")  # turuncu
        self.schema_box.tag_configure("string",   foreground="#a6e3a1")  # yeşil
        self.schema_box.tag_configure("comment",  foreground=TEXT_SUB)

    # ── Event handler'lar ────────────────────────────────────────────────

    def _on_table_selected(self, event=None):
        table_name = self.table_var.get()
        if table_name and self.on_table_select:
            self.on_table_select(table_name)

    # ── Public API ───────────────────────────────────────────────────────

    def update_table_list(self, tables: list[str]):
        """
        Combobox'ı yeni tablo listesiyle günceller.
        Dönüşüm tamamlandığında App tarafından çağrılır.
        """
        self.table_combo["values"] = tables
        if tables:
            self.table_var.set(tables[0])
            if self.on_table_select:
                self.on_table_select(tables[0])

    def show_table_data(self, columns: list[str], rows: list[tuple]):
        """
        DataGrid'i verilen sütun ve satırlarla doldurur.
        App tarafından DB'den çekilen veriyle çağrılır.
        """
        # Eski veriyi temizle
        self.data_grid["columns"] = columns
        self.data_grid.delete(*self.data_grid.get_children())

        for col in columns:
            self.data_grid.heading(col, text=col, anchor="w")
            # Sütun genişliğini sınırla — çok sütunda taşmasın
            width = max(len(col) * 9, 70)
            width = min(width, 140)   # maksimum 140px
            self.data_grid.column(col, width=width, minwidth=50, stretch=True)

        for i, row in enumerate(rows):
            tag = "even" if i % 2 == 0 else "odd"
            self.data_grid.insert("", "end", values=row, tags=(tag,))

        # İstatistik güncelle
        self.stat_label.configure(
            text=f"{len(rows)} satır · {len(columns)} sütun"
        )

    def show_schema_sql(self, sql: str):
        """
        SQL Şeması sekmesine CREATE TABLE metnini yazar.
        Basit syntax renklendirme uygular.
        """
        self.schema_box.configure(state="normal")
        self.schema_box.delete("1.0", "end")
        self.schema_box.insert("end", sql)
        self._highlight_sql()
        self.schema_box.configure(state="disabled")

    def clear(self):
        """Paneli sıfırlar."""
        self.table_combo["values"] = []
        self.table_var.set("")
        self.data_grid["columns"] = []
        self.data_grid.delete(*self.data_grid.get_children())
        self.stat_label.configure(text="")
        self.schema_box.configure(state="normal")
        self.schema_box.delete("1.0", "end")
        self.schema_box.configure(state="disabled")

    # ── Yardımcı metodlar ────────────────────────────────────────────────

    def _highlight_sql(self):
        """
        SQL metninde anahtar kelimeleri renklendirir.
        Basit string eşleşmesi kullanır — tam parser değil.
        """
        import re

        keywords = [
            "CREATE", "TABLE", "IF", "NOT", "EXISTS",
            "PRIMARY", "KEY", "FOREIGN", "REFERENCES",
            "AUTOINCREMENT", "DEFAULT", "NULL", "ON", "DELETE", "CASCADE"
        ]
        types = ["INTEGER", "TEXT", "REAL", "BLOB", "NUMERIC"]

        content = self.schema_box.get("1.0", "end")

        for kw in keywords:
            start = "1.0"
            while True:
                pos = self.schema_box.search(
                    kw, start, stopindex="end",
                    nocase=False, regexp=False
                )
                if not pos:
                    break
                end = f"{pos}+{len(kw)}c"
                self.schema_box.tag_add("keyword", pos, end)
                start = end

        for tp in types:
            start = "1.0"
            while True:
                pos = self.schema_box.search(tp, start, stopindex="end")
                if not pos:
                    break
                end = f"{pos}+{len(tp)}c"
                self.schema_box.tag_add("type", pos, end)
                start = end