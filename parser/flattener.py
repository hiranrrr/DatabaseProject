"""
flattener.py
------------
İç içe geçmiş (nested) JSON objelerini tek seviyeli düz bir dict'e
dönüştürür. Array (dizi) yapılarına DOKUNMAZ — onlar normalizer.py'ın işi.

Örnek:
    Girdi:
        {
            "ad": "Ahmet",
            "adres": {
                "sehir": "Kocaeli",
                "ilce": {
                    "ad": "İzmit",
                    "posta_kodu": "41000"
                }
            }
        }

    Çıktı:
        {
            "ad": "Ahmet",
            "adres_sehir": "Kocaeli",
            "adres_ilce_ad": "İzmit",
            "adres_ilce_posta_kodu": "41000"
        }
"""


def flatten(data: dict, parent_key: str = "", separator: str = "_") -> dict:
    """
    Tek bir JSON objesini (dict) özyinelemeli olarak düzleştirir.
    Sadece primitive değerler ve diziler sonuca eklenir;
    iç içe objeler anahtar birleştirilerek açılır.

    Parametreler:
        data      : Düzleştirilecek JSON dict'i
        parent_key: Üst seviyeden gelen anahtar öneki (özyineleme için)
        separator : Anahtarları birleştirme karakteri (varsayılan "_")

    Döndürür:
        dict: Düzleştirilmiş anahtar-değer çiftleri
              Değer bir list ise, o anahtar-değer çifti olduğu gibi bırakılır
              (diziler normalizer.py tarafından işlenecek)

    Örnek:
        flatten({"a": {"b": 1, "c": 2}})
        → {"a_b": 1, "a_c": 2}
    """
    result = {}

    for key, value in data.items():
        # Üst anahtar varsa birleştir: "adres" + "_" + "sehir" → "adres_sehir"
        new_key = f"{parent_key}{separator}{key}" if parent_key else key

        if isinstance(value, dict):
            # İç içe obje → özyinelemeli olarak aç
            nested = flatten(value, new_key, separator)
            result.update(nested)

        elif isinstance(value, list):
            # Dizi → olduğu gibi bırak, normalizer işleyecek
            result[new_key] = value

        else:
            # Primitive değer → doğrudan ekle
            result[new_key] = value

    return result


def flatten_list(records: list, separator: str = "_") -> list:
    """
    Birden fazla JSON objesinden oluşan bir listeyi düzleştirir.
    Her eleman için flatten() çağırır.

    Parametre:
        records  : dict'lerden oluşan liste
        separator: Anahtar birleştirme karakteri

    Döndürür:
        list[dict]: Her elemanı düzleştirilmiş liste

    Örnek:
        flatten_list([
            {"ad": "Ali", "adres": {"sehir": "Ankara"}},
            {"ad": "Veli", "adres": {"sehir": "İzmir"}},
        ])
        →
        [
            {"ad": "Ali",  "adres_sehir": "Ankara"},
            {"ad": "Veli", "adres_sehir": "İzmir"},
        ]
    """
    return [
        flatten(record, separator=separator)
        if isinstance(record, dict) else record
        for record in records
    ]


def extract_arrays(flat_data: dict) -> tuple[dict, dict]:
    """
    Düzleştirilmiş bir dict içindeki dizi (list) değerlerini ayırır.

    Döndürür:
        tuple(primitives, arrays)
            primitives: Dizi olmayan anahtar-değer çiftleri  (ana tablo sütunları)
            arrays    : Dizi olan anahtar-değer çiftleri     (alt tablolar için)

    Örnek:
        flat = {
            "ad": "Ahmet",
            "yas": 30,
            "siparisler": [{"urun": "kitap"}, {"urun": "kalem"}]
        }
        primitives, arrays = extract_arrays(flat)
        primitives → {"ad": "Ahmet", "yas": 30}
        arrays     → {"siparisler": [{"urun": "kitap"}, {"urun": "kalem"}]}
    """
    primitives = {}
    arrays = {}

    for key, value in flat_data.items():
        if isinstance(value, list):
            arrays[key] = value
        else:
            primitives[key] = value

    return primitives, arrays