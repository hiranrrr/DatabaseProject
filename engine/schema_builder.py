"""
schema_builder.py
-----------------
JSON verisini analiz ederek çalışma zamanında (runtime) SQL tablo şemalarını
dinamik olarak üretir. Hiçbir tablo adı veya sütun adı hardcoded değildir.

Bu modül gerçek SQL çalıştırmaz; sadece şema tarifini (TableSchema) üretir.
Gerçek SQL çalıştırma → db_manager.py'ın işi.
"""

from dataclasses import dataclass, field
from utils.type_mapper import get_sql_type, infer_dominant_type
from parser.flattener import flatten, extract_arrays


@dataclass
class ColumnSchema:
    """Tek bir SQL sütununu tanımlar."""
    name:        str
    sql_type:    str
    is_primary:  bool = False
    is_foreign:  bool = False
    foreign_ref: str  = ""   # "referans_tablo(id)" formatında

    def to_sql(self) -> str:
        """Sütunu CREATE TABLE içinde kullanılacak SQL ifadesine dönüştürür."""
        parts = [f'"{self.name}"', self.sql_type]

        if self.is_primary:
            parts.append("PRIMARY KEY AUTOINCREMENT")
        if self.is_foreign:
            # Foreign key kısıtı ayrıca eklenir, burada sadece tip
            pass
        if self.sql_type == "TEXT":
            parts.append("DEFAULT NULL")

        return " ".join(parts)


@dataclass
class TableSchema:
    """Tek bir SQL tablosunu tanımlar."""
    name:        str
    columns:     list = field(default_factory=list)   # list[ColumnSchema]
    foreign_keys: list = field(default_factory=list)  # list[str]  → SQL FK ifadeleri
    parent_table: str = ""   # FK ilişkisindeki üst tablo adı
    parent_key:   str = ""   # FK ilişkisindeki üst tablo primary key adı

    def add_column(self, col: ColumnSchema):
        self.columns.append(col)

    def to_create_sql(self) -> str:
        """
        Tam CREATE TABLE sorgusunu üretir.

        Örnek çıktı:
            CREATE TABLE IF NOT EXISTS "siparisler" (
                "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                "musteri_id" INTEGER DEFAULT NULL,
                "urun" TEXT DEFAULT NULL,
                FOREIGN KEY ("musteri_id") REFERENCES "musteriler"("id")
            );
        """
        lines = []
        for col in self.columns:
            lines.append(f"    {col.to_sql()}")

        for fk in self.foreign_keys:
            lines.append(f"    {fk}")

        body = ",\n".join(lines)
        return f'CREATE TABLE IF NOT EXISTS "{self.name}" (\n{body}\n);'


class SchemaBuilder:
    """
    JSON verisini alıp tüm tablo şemalarını dinamik olarak üretir.

    Kullanım:
        builder = SchemaBuilder()
        schemas = builder.build(data=json_data, root_table_name="musteriler")
        for schema in schemas:
            print(schema.to_create_sql())
    """

    def __init__(self, separator: str = "_"):
        self.separator = separator
        self.schemas: list[TableSchema] = []

    def build(self, data, root_table_name: str = "root") -> list[TableSchema]:
        """
        JSON verisinden tüm TableSchema nesnelerini üretir.

        Parametre:
            data            : JSON'dan yüklenen Python nesnesi (dict veya list)
            root_table_name : Ana tablonun adı (genellikle dosya adından türetilir)

        Döndürür:
            list[TableSchema]: Önce ana tablo, sonra alt tablolar
        """
        self.schemas = []

        # JSON doğrudan liste ise, liste elemanlarını kayıt olarak kabul et
        if isinstance(data, list):
            records = data
        else:
            records = [data]

        self._process_table(
            records=records,
            table_name=root_table_name,
            parent_table="",
            parent_key=""
        )

        return self.schemas

    def _process_table(
        self,
        records: list,
        table_name: str,
        parent_table: str,
        parent_key: str
    ):
        """
        Kayıt listesinden bir TableSchema üretir.
        İçindeki diziler için özyinelemeli olarak alt tablolar oluşturur.
        """
        schema = TableSchema(
            name=table_name,
            parent_table=parent_table,
            parent_key=parent_key
        )

        # 1. Primary key her tabloya otomatik eklenir
        pk_col = ColumnSchema(
            name="id",
            sql_type="INTEGER",
            is_primary=True
        )
        schema.add_column(pk_col)

        # 2. Eğer alt tablo ise, üst tabloya FK ekle
        if parent_table and parent_key:
            fk_col_name = f"{parent_table}_id"
            fk_col = ColumnSchema(
                name=fk_col_name,
                sql_type="INTEGER",
                is_foreign=True,
                foreign_ref=f'"{parent_table}"("{parent_key}")'
            )
            schema.add_column(fk_col)
            schema.foreign_keys.append(
                f'FOREIGN KEY ("{fk_col_name}") REFERENCES "{parent_table}"("{parent_key}")'
            )

        # 3. Tüm kayıtları tara, sütun adlarını ve tiplerini topla
        column_values: dict[str, list] = {}  # sütun_adı → [değerler]
        child_arrays: dict[str, list] = {}   # dizi_adı → [tüm dizi elemanları]

        for record in records:
            if not isinstance(record, dict):
                continue

            # Nested objeleri düzleştir, dizileri ayır
            flat = flatten(record, separator=self.separator)
            primitives, arrays = extract_arrays(flat)

            # Primitive sütunları topla
            for col_name, value in primitives.items():
                col_name_clean = self._sanitize_name(col_name)
                if col_name_clean not in column_values:
                    column_values[col_name_clean] = []
                column_values[col_name_clean].append(value)

            # Dizileri topla (alt tablo oluşturulacak)
            for arr_name, arr_value in arrays.items():
                arr_name_clean = self._sanitize_name(arr_name)
                if arr_name_clean not in child_arrays:
                    child_arrays[arr_name_clean] = []
                child_arrays[arr_name_clean].extend(arr_value)

        # 4. Topladığımız sütunları şemaya ekle
        for col_name, values in column_values.items():
            dominant_type = infer_dominant_type(values)
            col = ColumnSchema(name=col_name, sql_type=dominant_type)
            schema.add_column(col)

        self.schemas.append(schema)

        # 5. Diziler için özyinelemeli alt tablo oluştur
        for arr_name, arr_records in child_arrays.items():
            self._process_table(
                records=arr_records,
                table_name=arr_name,
                parent_table=table_name,
                parent_key="id"
            )

    def _sanitize_name(self, name: str) -> str:
        """
        Sütun/tablo adını SQL için güvenli hale getirir.
        Boşlukları ve özel karakterleri alt çizgiye çevirir.
        """
        import re
        name = name.strip().lower()
        name = re.sub(r"[^\w]", "_", name)   # harf/rakam/_ dışındakileri _ yap
        name = re.sub(r"_+", "_", name)       # tekrar eden _ → tek _
        name = name.strip("_")
        return name