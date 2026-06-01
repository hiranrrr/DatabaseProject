# iç içe objeleri düzleştirir, adres sehir iç içe ise adres_sehir yapar 
def flatten(data: dict, parent_key: str = "", separator: str = "_") -> dict:

    result = {}

    for key, value in data.items():
       
        new_key = f"{parent_key}{separator}{key}" if parent_key else key

        if isinstance(value, dict):
            nested = flatten(value, new_key, separator)
            result.update(nested)

        elif isinstance(value, list):
            result[new_key] = value

        else:
            result[new_key] = value

    return result

#liste dondurur
def flatten_list(records: list, separator: str = "_") -> list:

    return [
        flatten(record, separator=separator)
        if isinstance(record, dict) else record
        for record in records
    ]

# Düzleştirilmiş veriyi primitives (ilkel değerler) ve arrays (listeler) olarak ayırır
def extract_arrays(flat_data: dict) -> tuple[dict, dict]:
    primitives = {}
    arrays = {}

    for key, value in flat_data.items():
        if isinstance(value, list):
            arrays[key] = value
        else:
            primitives[key] = value

    return primitives, arrays