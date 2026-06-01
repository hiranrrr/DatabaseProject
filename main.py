import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from tkinter import messagebox

import ui.styles as styles
from ui.json_panel    import JsonPanel
from ui.control_panel import ControlPanel
from ui.sql_panel     import SqlPanel

from engine.schema_builder import SchemaBuilder
from engine.normalizer     import Normalizer
from database.db_manager   import DatabaseManager


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NoSQL → SQL Dönüşüm Sistemi")
        self.geometry("1300x800")
        self.minsize(1050, 620)
        self.configure(bg=styles.BG_DARK)

        self.db = DatabaseManager("converted.db")

        styles.apply(self)
        self._build_header()
        self._build_panels()

    def _build_header(self):
        header = tk.Frame(self, bg=styles.ACCENT, height=48)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="  🔄  NoSQL → SQL Dönüşüm Sistemi  |  Kocaeli Üniversitesi",
            bg=styles.ACCENT, fg="#ffffff",
            font=("Segoe UI", 12, "bold")
        ).pack(side="left", pady=12)

    def _build_panels(self):
        content = tk.Frame(self, bg=styles.BG_DARK)
        content.pack(fill="both", expand=True, padx=12, pady=12)

        content.columnconfigure(0, weight=3, minsize=260)   # JSON paneli
        content.columnconfigure(1, weight=0, minsize=150)   # İşlemler — sabit dar
        content.columnconfigure(2, weight=7, minsize=420)   # SQL paneli
        content.rowconfigure(0, weight=1)

        self.json_panel = JsonPanel(
            content,
            on_loaded=self._on_json_loaded,
            on_error =self._on_error
        )
        self.json_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        self.control_panel = ControlPanel(
            content,
            on_convert=self._on_convert,
            on_reset  =self._on_reset
        )
        self.control_panel.grid(row=0, column=1, sticky="nsew", padx=6)

        self.sql_panel = SqlPanel(
            content,
            on_table_select=self._on_table_selected,
            on_query_run   =self._on_query_run
        )
        self.sql_panel.grid(row=0, column=2, sticky="nsew", padx=(6, 0))

    def _on_json_loaded(self, data, filepath: str):
        fname = os.path.basename(filepath)
        self.control_panel.log(f"✅ Dosya yüklendi: {fname}", "success")
        self.control_panel.log(
            f"   Tip: {'liste' if isinstance(data, list) else 'nesne'}"
            + (f" · {len(data)} kayıt" if isinstance(data, list) else ""),
            "info"
        )

    def _on_error(self, message: str):
        self.control_panel.log(f"❌ {message}", "error")
        messagebox.showerror("Hata", message)

    def _on_convert(self):
        data     = self.json_panel.get_data()
        filepath = self.json_panel.get_filepath()

        if data is None:
            messagebox.showwarning("Uyarı", "Önce bir JSON dosyası seçin.")
            return

        try:
            base      = os.path.splitext(os.path.basename(filepath))[0]
            root_name = self._sanitize(base) or "tablo"

            self.control_panel.log("─" * 32, "info")

            self.db.connect()
            self.db.reset()
            self.sql_panel.clear()

            self.control_panel.log("🔍 Şema analiz ediliyor...", "info")

            builder = SchemaBuilder()
            schemas = builder.build(data, root_table_name=root_name)

            for s in schemas:
                col_names = [c.name for c in s.columns]
                self.control_panel.log(f"   📋 {s.name}: {col_names}", "info")

            self.db.connect()
            self.db.create_tables(schemas)
            self.control_panel.log("✅ Tablolar oluşturuldu.", "success")

            self.control_panel.log("📥 Veri aktarılıyor...", "info")
            normalizer = Normalizer(schemas)
            insert_ops = normalizer.generate_inserts(data, root_name)
            self.db.insert_all(insert_ops)
            self.control_panel.log(f"✅ {len(insert_ops)} satır aktarıldı.", "success")

            tables = self.db.get_all_tables()
            self.sql_panel.update_table_list(tables)

        except Exception as e:
            self.control_panel.log(f"❌ Dönüşüm hatası: {e}", "error")
            messagebox.showerror("Dönüşüm Hatası", str(e))

    def _on_reset(self):
        if not messagebox.askyesno("Sıfırla", "Tüm tablolar silinecek. Emin misiniz?"):
            return
        try:
            self.db.connect()
            self.db.reset()
            self.json_panel.clear()
            self.sql_panel.clear()
            self.control_panel.clear_log()
            self.control_panel.log("🗑️  Sistem sıfırlandı.", "warning")
        except Exception as e:
            self._on_error(str(e))

    def _on_table_selected(self, table_name: str):
        try:
            columns, rows = self.db.get_table_data(table_name)
            self.sql_panel.show_table_data(columns, rows)
            schema_sql = self.db.get_table_schema_sql(table_name)
            self.sql_panel.show_schema_sql(schema_sql)
        except Exception as e:
            self.control_panel.log(f"❌ Tablo gösterme hatası: {e}", "error")

    def _on_query_run(self, sql: str):
        # Kullanıcının yazdığı SQL sorgusunu çalıştırır, sonucu panelde gösterir
        try:
            columns, rows = self.db.execute_query(sql)
            self.sql_panel.show_query_result(columns, rows)
        except Exception as e:
            self.sql_panel.show_query_error(str(e))

    def _sanitize(self, name: str) -> str:
        import re
        name = name.strip().lower()
        name = re.sub(r"[^\w]", "_", name)
        name = re.sub(r"_+", "_", name)
        return name.strip("_")


if __name__ == "__main__":
    app = App()
    app.mainloop()