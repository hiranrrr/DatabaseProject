# Python tipi → SQLite tipi eşlemesi
# JSON verisinden SQL şeması oluştururken Python veri tiplerini uygun SQLite veri tiplerine dönüştürmek için kullanılır
TYPE_MAP = {
    int:   "INTEGER",
    float: "REAL",
    bool:  "INTEGER",
    str:   "TEXT",
    type(None): "TEXT", 
}

def get_sql_type(value) -> str:
    return TYPE_MAP.get(type(value), "TEXT")

def get_sql_type_from_python_type(python_type: type) -> str:
    return TYPE_MAP.get(python_type, "TEXT")

def infer_dominant_type(values: list) -> str:
   
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