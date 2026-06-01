import json
from pathlib import Path

# JSON dosyasını okuyup yapısını analiz eder
#Verilen dosya yolundaki JSON dosyasını okur ve Python nesnesine dönüştürür.
def load_json(filepath: str) -> any:
   
    path = Path(filepath)

    if not path.exists():
        raise FileNotFoundError(f"Dosya bulunamadı: {filepath}")

    if not path.suffix.lower() == ".json":
        raise ValueError(f"Dosya JSON formatında olmalıdır: {filepath}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data


def detect_value_type(value) -> str:

    if isinstance(value, dict):
        return "object"
    elif isinstance(value, list):
        return "array"
    else:
        return "primitive"

# JSON yapısını analiz eder ve her elemanın türünü, yolunu ve değerini raporlar
def analyze_structure(data, indent: int = 0) -> list:
 
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

            if isinstance(value, dict):
                sub_report = analyze_structure(value, indent + 1)
                for sub in sub_report:
                    sub["path"] = f"{key}.{sub['path']}"  # yolu birleştir
                report.extend(sub_report)

            elif isinstance(value, list) and len(value) > 0:
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

# JSON verisini okunabilir formatta döndürür
def pretty_print(data, indent: int = 2) -> str:

    return json.dumps(data, ensure_ascii=False, indent=indent)