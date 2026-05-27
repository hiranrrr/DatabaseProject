"""
normalizer.py
-------------
JSON verisini şema bilgisiyle eşleştirip INSERT INTO sorgularını üretir.
Her kayıt için önce ana tabloya, sonra alt tablolara sırasıyla veri yazar.

Bu modül SQL çalıştırmaz; sadece (tablo_adı, sütunlar, değerler) üçlülerini
üretir.
"""

from parser.flattener import flatten, extract_arrays
from engine.schema_builder import TableSchema


class Normalizer:
    """
    JSON kayıtlarını tablo şemalarına göre normalize eder ve
    INSERT komutları için hazır veri paketleri üretir.

    Kullanım:
        normalizer = Normalizer(schemas)
        insert_ops = normalizer.generate_inserts(data, root_table_name)
        # insert_ops → [(tablo_adı, {sütun: değer}), ...]
    """

    def __init__(self, schemas: list[TableSchema], separator: str = "_"):
        # Tablo adı → TableSchema eşlemesi
        self.schema_map: dict[str, TableSchema] = {s.name: s for s in schemas}
        self.separator = separator
        self.insert_ops: list[tuple[str, dict]] = []  # (tablo_adı, {col: val})

    def generate_inserts(self, data, root_table_name: str) -> list[tuple[str, dict]]:
        """
        Tüm JSON verisini dolaşarak INSERT operasyonlarını üretir.

        Döndürür:
            list[ (tablo_adı: str, row_data: dict) ]
            Her eleman bir INSERT satırını temsil eder.
        """
        self.insert_ops = []

        records = data if isinstance(data, list) else [data]

        for record in records:
            self._process_record(
                record=record,
                table_name=root_table_name,
                parent_id=None,
                parent_table=""
            )

        return self.insert_ops

    def _process_record(
        self,
        record,
        table_name: str,
        parent_id,          # üst tablodaki satırın id değeri (int veya None)
        parent_table: str
    ) -> int:
        """
        Tek bir kaydı işler:
        1. Nested objeleri düzleştirir
        2. Primitive değerleri ana tabloya yazar
        3. Dizileri alır, her elemanı alt tabloya özyinelemeli yazar

        Döndürür:
            int: Bu kaydın INSERT sırasındaki sıra numarası (FK için kullanılır)
                 Gerçek id db_manager tarafından lastrowid ile alınır.
                 Bu değer placeholder olarak kullanılır.
        """
        if not isinstance(record, dict):
            return -1

        schema = self.schema_map.get(table_name)
        if schema is None:
            return -1

        # 1. Düzleştir ve dizileri ayır
        flat = flatten(record, separator=self.separator)
        primitives, arrays = extract_arrays(flat)

        # 2. Şemadaki sütunlarla eşleştir (sadece var olan sütunlara yaz)
        schema_col_names = {col.name for col in schema.columns
                            if not col.is_primary}

        row_data = {}

        # FK sütunu varsa parent_id'yi ekle
        if parent_table and parent_id is not None:
            fk_col = f"{parent_table}_id"
            if fk_col in schema_col_names:
                row_data[fk_col] = parent_id

        # Primitive değerleri ekle
        for raw_key, value in primitives.items():
            col_name = self._sanitize_name(raw_key)
            if col_name in schema_col_names:
                row_data[col_name] = value

        # 3. Bu satırın INSERT operasyonunu kaydet
        row_index = len(self.insert_ops)
        self.insert_ops.append((table_name, row_data))

        # 4. Diziler için alt tablo işlemi
        for arr_key, arr_records in arrays.items():
            child_table_name = self._sanitize_name(arr_key)

            if child_table_name not in self.schema_map:
                continue

            for child_record in arr_records:
                self._process_record(
                    record=child_record,
                    table_name=child_table_name,
                    parent_id=row_index,   # db_manager bunu gerçek id ile değiştirir
                    parent_table=table_name
                )

        return row_index

    def _sanitize_name(self, name: str) -> str:
        import re
        name = name.strip().lower()
        name = re.sub(r"[^\w]", "_", name)
        name = re.sub(r"_+", "_", name)
        name = name.strip("_")
        return name