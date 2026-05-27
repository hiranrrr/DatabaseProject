"""
type_mapper.py
--------------
Python veri tiplerini SQLite veri tiplerine dönüştüren yardımcı modül.
Tüm sistem bu modülü kullanarak sütun tiplerini belirler.
"""


# Python tipi → SQLite tipi eşlemesi
TYPE_MAP = {
    int:   "INTEGER",
    float: "REAL",
    bool:  "INTEGER",   # SQLite'ta boolean yoktur; 0/1 olarak tutulur
    str:   "TEXT",
    type(None): "TEXT", # NULL değerler TEXT olarak tanımlanır
}


def get_sql_type(value) -> str:
    """
    Verilen Python değerine bakarak uygun SQLite tipini döndürür.

    Parametre:
        value: JSON'dan okunan herhangi bir değer (str, int, float, bool, None)

    Döndürür:
        str: SQLite tip adı ("TEXT", "INTEGER", "REAL")

    Örnek:
        get_sql_type(42)        → "INTEGER"
        get_sql_type(3.14)      → "REAL"
        get_sql_type("merhaba") → "TEXT"
        get_sql_type(True)      → "INTEGER"
        get_sql_type(None)      → "TEXT"
    """
    return TYPE_MAP.get(type(value), "TEXT")


def get_sql_type_from_python_type(python_type: type) -> str:
    """
    Python tip nesnesine bakarak uygun SQLite tipini döndürür.
    (Değer yerine tip sınıfı verildiğinde kullanılır.)

    Parametre:
        python_type: type nesnesi (örn: int, str, float)

    Döndürür:
        str: SQLite tip adı

    Örnek:
        get_sql_type_from_python_type(int)   → "INTEGER"
        get_sql_type_from_python_type(float) → "REAL"
        get_sql_type_from_python_type(str)   → "TEXT"
    """
    return TYPE_MAP.get(python_type, "TEXT")


def infer_dominant_type(values: list) -> str:
    """
    Bir listedeki değerlere bakarak baskın SQL tipini belirler.
    Aynı anahtar için farklı JSON nesnelerinde farklı tipler görülebilir;
    bu fonksiyon en kapsayıcı tipi seçer.

    Öncelik sırası (en kapsayıcıdan en dara):
        TEXT > REAL > INTEGER

    Parametre:
        values: Aynı anahtardan toplanan değerlerin listesi

    Döndürür:
        str: Baskın SQLite tip adı

    Örnek:
        infer_dominant_type([1, 2, 3])         → "INTEGER"
        infer_dominant_type([1, 2.5, 3])       → "REAL"
        infer_dominant_type([1, "hello", 3])   → "TEXT"
        infer_dominant_type([])                → "TEXT"
    """
    if not values:
        return "TEXT"

    sql_types = set()

    for value in values:
        if value is None:
            continue  # None'ları atlıyoruz, diğer değerler tipi belirlesin
        sql_types.add(get_sql_type(value))

    # Öncelik sırası: TEXT > REAL > INTEGER
    if "TEXT" in sql_types:
        return "TEXT"
    if "REAL" in sql_types:
        return "REAL"
    if "INTEGER" in sql_types:
        return "INTEGER"

    return "TEXT"  # Tüm değerler None ise varsayılan