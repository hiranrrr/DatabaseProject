import tkinter as tk
from tkinter import ttk

from ui.styles import (
    BG_PANEL, BG_WIDGET,
    ACCENT, TEXT_MAIN, TEXT_SUB, SUCCESS, ERROR
)

# SQL sonuçlarını ve şemalarını göstermek için sağ panel 
class SqlPanel(ttk.Frame):

    def __init__(self, parent, on_table_select=None, on_query_run=None, **kwargs):
        super().__init__(parent, style="Panel.TFrame", **kwargs)

        self.on_table_select = on_table_select
        self.on_query_run    = on_query_run 

        self._build()

    def _build(self):
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)

        ttk.Label(self, text="🗃️  SQL Tabloları", style="Title.TLabel").grid(
            row=0, column=0, sticky="w", padx=12, pady=(12, 4)
        )

        # Tablo seçici satırı
        sel_row = ttk.Frame(self, style="Panel.TFrame")
        sel_row.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))

        ttk.Label(sel_row, text="Tablo:", style="TLabel").pack(side="left")

        self.table_var = tk.StringVar()
        self.table_combo = ttk.Combobox(
            sel_row, textvariable=self.table_var,
            state="readonly", width=22
        )
        self.table_combo.pack(side="left", padx=(8, 12))
        self.table_combo.bind("<<ComboboxSelected>>", self._on_table_selected)

        self.stat_label = ttk.Label(sel_row, text="", style="Sub.TLabel")
        self.stat_label.pack(side="left")

        # 3 bolum 
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=2, column=0, sticky="nsew", padx=12, pady=(0, 12))

        self._build_data_tab()#1 Tablo verisi
        self._build_schema_tab() #2 CREATE TABLE SQL şeması
        self._build_query_tab()  #3 Kullanıcı SQL sorgusu,sonucu ve hatalar

    def _build_data_tab(self):
        
        data_tab = ttk.Frame(self.notebook, style="Panel.TFrame")
        data_tab.rowconfigure(0, weight=1)
        data_tab.columnconfigure(0, weight=1)
        self.notebook.add(data_tab, text="  📄 Veri  ")

        self.data_grid = ttk.Treeview(data_tab, show="headings")
        grid_vsb = ttk.Scrollbar(data_tab, orient="vertical",   command=self.data_grid.yview)
        grid_hsb = ttk.Scrollbar(data_tab, orient="horizontal", command=self.data_grid.xview)
        self.data_grid.configure(yscrollcommand=grid_vsb.set, xscrollcommand=grid_hsb.set)

        self.data_grid.grid(row=0, column=0, sticky="nsew")
        grid_vsb.grid(row=0, column=1, sticky="ns")
        grid_hsb.grid(row=1, column=0, sticky="ew")

        self.data_grid.tag_configure("odd",  background=BG_WIDGET)
        self.data_grid.tag_configure("even", background="#655b63")

    def _build_schema_tab(self):
       
        schema_tab = ttk.Frame(self.notebook, style="Panel.TFrame")
        schema_tab.rowconfigure(0, weight=1)
        schema_tab.columnconfigure(0, weight=1)
        self.notebook.add(schema_tab, text="  🔧 SQL Şeması  ")

        self.schema_box = tk.Text(
            schema_tab,
            bg=BG_WIDGET, fg="#c1d566",
            font=("Consolas", 9),
            wrap="none", state="disabled", relief="flat",
            insertbackground=TEXT_MAIN
        )
        schema_vsb = ttk.Scrollbar(schema_tab, orient="vertical",   command=self.schema_box.yview)
        schema_hsb = ttk.Scrollbar(schema_tab, orient="horizontal", command=self.schema_box.xview)
        self.schema_box.configure(yscrollcommand=schema_vsb.set, xscrollcommand=schema_hsb.set)

        self.schema_box.grid(row=0, column=0, sticky="nsew")
        schema_vsb.grid(row=0, column=1, sticky="ns")
        schema_hsb.grid(row=1, column=0, sticky="ew")

        self.schema_box.tag_configure("keyword", foreground="#59d437")
        self.schema_box.tag_configure("type",    foreground="#805235")

    def _build_query_tab(self):
       
        query_tab = ttk.Frame(self.notebook, style="Panel.TFrame")
        query_tab.rowconfigure(1, weight=1)
        query_tab.columnconfigure(0, weight=1)
        self.notebook.add(query_tab, text="  🔍 SQL Sorgula  ")

        # Sorgu giriş alanı + buton
        input_frame = tk.Frame(query_tab, bg=BG_PANEL)
        input_frame.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        input_frame.columnconfigure(0, weight=1)

        self.query_input = tk.Text(
            input_frame,
            bg=BG_WIDGET, fg="#8ed566",
            font=("Consolas", 10),
            height=4, relief="flat",
            insertbackground=TEXT_MAIN,
            wrap="word"
        )
        self.query_input.grid(row=0, column=0, sticky="ew", pady=(0, 6))

        self.query_input.bind("<Control-Return>", lambda e: self._run_query())

        btn_row = tk.Frame(input_frame, bg=BG_PANEL)
        btn_row.grid(row=1, column=0, sticky="ew")

        ttk.Button(
            btn_row, text="▶  Sorguyu Çalıştır",
            style="Accent.TButton",
            command=self._run_query
        ).pack(side="left", padx=(0, 12))

        ttk.Button(
            btn_row, text="Temizle",
            command=self._clear_query
        ).pack(side="left")

        self.query_stat = tk.Label(
            btn_row, text="", bg=BG_PANEL, fg=TEXT_SUB,
            font=("Segoe UI", 9)
        )
        self.query_stat.pack(side="left", padx=12)

        # Sonuç grid
        result_frame = tk.Frame(query_tab, bg=BG_PANEL)
        result_frame.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        result_frame.rowconfigure(0, weight=1)
        result_frame.columnconfigure(0, weight=1)

        self.query_grid = ttk.Treeview(result_frame, show="headings")
        q_vsb = ttk.Scrollbar(result_frame, orient="vertical",   command=self.query_grid.yview)
        q_hsb = ttk.Scrollbar(result_frame, orient="horizontal", command=self.query_grid.xview)
        self.query_grid.configure(yscrollcommand=q_vsb.set, xscrollcommand=q_hsb.set)

        self.query_grid.grid(row=0, column=0, sticky="nsew")
        q_vsb.grid(row=0, column=1, sticky="ns")
        q_hsb.grid(row=1, column=0, sticky="ew")

        self.query_grid.tag_configure("odd",  background=BG_WIDGET)
        self.query_grid.tag_configure("even", background="#38384e")

        self.query_input.insert("1.0", "SELECT * FROM ")

    def _on_table_selected(self, event=None):
        table_name = self.table_var.get()
        if table_name and self.on_table_select:
            self.on_table_select(table_name)

    def _run_query(self):
        sql = self.query_input.get("1.0", "end").strip()
        if not sql:
            return
        if self.on_query_run:
            self.on_query_run(sql)

    def _clear_query(self):
        self.query_input.delete("1.0", "end")
        self.query_grid["columns"] = []
        self.query_grid.delete(*self.query_grid.get_children())
        self.query_stat.configure(text="")

    def update_table_list(self, tables: list[str]):
        self.table_combo["values"] = tables
        if tables:
            self.table_var.set(tables[0])
            if self.on_table_select:
                self.on_table_select(tables[0])

    def show_table_data(self, columns: list[str], rows: list[tuple]):
        self.data_grid["columns"] = columns
        self.data_grid.delete(*self.data_grid.get_children())

        for col in columns:
            self.data_grid.heading(col, text=col, anchor="w")
            width = min(max(len(col) * 9, 70), 140)
            self.data_grid.column(col, width=width, minwidth=50, stretch=True)

        for i, row in enumerate(rows):
            tag = "even" if i % 2 == 0 else "odd"
            self.data_grid.insert("", "end", values=row, tags=(tag,))

        self.stat_label.configure(text=f"{len(rows)} satır · {len(columns)} sütun")
    
    # Sorgu sonucunu query_grid'e doldurur
    def show_query_result(self, columns: list[str], rows: list[tuple]):
        
        self.query_grid["columns"] = columns
        self.query_grid.delete(*self.query_grid.get_children())

        for col in columns:
            self.query_grid.heading(col, text=col, anchor="w")
            width = min(max(len(col) * 9, 70), 160)
            self.query_grid.column(col, width=width, minwidth=50, stretch=True)

        for i, row in enumerate(rows):
            tag = "even" if i % 2 == 0 else "odd"
            self.query_grid.insert("", "end", values=row, tags=(tag,))

        self.query_stat.configure(
            text=f"✅ {len(rows)} satır döndü",
            fg=SUCCESS
        )

    def show_query_error(self, message: str):
        self.query_grid["columns"] = []
        self.query_grid.delete(*self.query_grid.get_children())
        self.query_stat.configure(text=f"❌ {message}", fg=ERROR)

    def show_schema_sql(self, sql: str):
        self.schema_box.configure(state="normal")
        self.schema_box.delete("1.0", "end")
        self.schema_box.insert("end", sql)
        self._highlight_sql()
        self.schema_box.configure(state="disabled")

    def clear(self):
        self.table_combo["values"] = []
        self.table_var.set("")
        self.data_grid["columns"] = []
        self.data_grid.delete(*self.data_grid.get_children())
        self.stat_label.configure(text="")
        self.schema_box.configure(state="normal")
        self.schema_box.delete("1.0", "end")
        self.schema_box.configure(state="disabled")
        self._clear_query()

    def _highlight_sql(self):
        keywords = [
            "CREATE", "TABLE", "IF", "NOT", "EXISTS",
            "PRIMARY", "KEY", "FOREIGN", "REFERENCES",
            "AUTOINCREMENT", "DEFAULT", "NULL", "ON", "DELETE", "CASCADE"
        ]
        types = ["INTEGER", "TEXT", "REAL", "BLOB", "NUMERIC"]

        for kw in keywords:
            start = "1.0"
            while True:
                pos = self.schema_box.search(kw, start, stopindex="end")
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