"""
json_parser.py
--------------
JSON dosyasını diskten okur, belleğe yükler ve
içindeki her anahtarın veri tipini raporlar.

Bu modül sadece OKUMA ve TESPİT yapar.
Düzleştirme (flattening) ve normalizasyon başka modüllerde yapılır.
"""

import json
from pathlib import Path


def load_json(filepath: str) -> any:
    """
    Verilen dosya yolundaki JSON dosyasını okur ve Python nesnesine dönüştürür.

    Parametre:
        filepath: JSON dosyasının tam yolu (str veya Path)

    Döndürür:
        dict | list: JSON içeriği Python nesnesi olarak

    Hata fırlatır:
        FileNotFoundError : Dosya bulunamazsa
        json.JSONDecodeError: Geçersiz JSON formatında ise
    """
    path = Path(filepath)

    if not path.exists():
        raise FileNotFoundError(f"Dosya bulunamadı: {filepath}")

    if not path.suffix.lower() == ".json":
        raise ValueError(f"Dosya JSON formatında olmalıdır: {filepath}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data


def detect_value_type(value) -> str:
    """
    Tek bir değerin kategorisini döndürür.

    Kategoriler:
        "primitive"  → str, int, float, bool, None
        "object"     → dict (iç içe nesne)
        "array"      → list (dizi)

    Parametre:
        value: JSON'dan gelen herhangi bir değer

    Döndürür:
        str: "primitive" | "object" | "array"
    """
    if isinstance(value, dict):
        return "object"
    elif isinstance(value, list):
        return "array"
    else:
        return "primitive"


def analyze_structure(data, indent: int = 0) -> list:
    """
    JSON verisini özyinelemeli (recursive) olarak dolaşır ve
    her anahtarın yolunu + tipini raporlar.

    Parametre:
        data  : JSON'dan gelen dict veya list
        indent: Hiyerarşi derinliği (görsel raporlama için)

    Döndürür:
        list[dict]: Her eleman şu anahtarları içerir:
            - path  : Anahtarın tam yolu (örn: "adres.sehir")
            - type  : "primitive" | "object" | "array"
            - value : Değerin kendisi (primitive ise) veya özet
            - depth : Kaç seviye derinlikte olduğu
    """
    report = []

    if isinstance(data, dict):
        for key, value in data.items():
            entry = {
                "path":  key,
                "type":  detect_value_type(value),
                "value": value if detect_value_type(value) == "primitive" else f"<{detect_value_type(value)}>",
                "depth": indent,
            }
            report.append(entry)

            # Özyinelemeli: alt seviyeleri de analiz et
            if isinstance(value, dict):
                sub_report = analyze_structure(value, indent + 1)
                for sub in sub_report:
                    sub["path"] = f"{key}.{sub['path']}"  # yolu birleştir
                report.extend(sub_report)

            elif isinstance(value, list) and len(value) > 0:
                # Dizinin ilk elemanını temsil olarak analiz et
                first_item = value[0]
                if isinstance(first_item, dict):
                    sub_report = analyze_structure(first_item, indent + 1)
                    for sub in sub_report:
                        sub["path"] = f"{key}[].{sub['path']}"
                    report.extend(sub_report)

    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, dict):
                sub_report = analyze_structure(item, indent)
                report.extend(sub_report)

    return report


def pretty_print(data, indent: int = 2) -> str:
    """
    JSON verisini okunabilir formatlı string'e dönüştürür.
    GUI'deki text alanında göstermek için kullanılır.

    Parametre:
        data  : dict veya list
        indent: Girinti boşluğu (varsayılan 2)

    Döndürür:
        str: Formatlı JSON metni
    """
    return json.dumps(data, ensure_ascii=False, indent=indent)