# NoSQL → SQL Dönüşüm Sistemi

## Kurulum

Python 3.10+ gereklidir. Ekstra kütüphane kurulumu **gerekmez** —
tüm modüller Python standart kütüphanesindedir (`tkinter`, `sqlite3`, `json`).

## Çalıştırma

```bash
cd json_to_sql
python main.py
```

## Proje Yapısı

```
json_to_sql/
├── main.py                        # GUI girişi
├── parser/
│   ├── json_parser.py             # JSON okuma + tip tespiti
│   └── flattener.py               # Nested obje düzleştirme
├── engine/
│   ├── schema_builder.py          # Dinamik CREATE TABLE şeması
│   └── normalizer.py              # INSERT operasyonları üretme
├── database/
│   └── db_manager.py              # SQLite bağlantı + sorgu çalıştırma
├── utils/
│   └── type_mapper.py             # Python tipi → SQL tipi
└── test_data/
    └── musteriler.json            # Örnek test verisi
```

## Kullanım

1. "Dosya Seç" → JSON dosyası yükle
2. Sol panelde JSON ağaç yapısını gözlemle
3. "Dönüştür" → sistem otomatik olarak:
   - Şemayı analiz eder
   - CREATE TABLE sorgularını üretir ve çalıştırır
   - INSERT INTO ile veriyi aktarır
4. Sağ panelden oluşturulan tabloları seç ve incele
5. "Sıfırla" → tüm tabloları temizle, yeni JSON dene

## Desteklenen JSON Yapıları

- Primitive değerler (string, int, float, bool, null)
- İç içe objeler (nested objects) → düzleştirme (flattening)
- Diziler (arrays) → otomatik alt tablo + Foreign Key
- Çok katmanlı (5-6 seviye derinlik) yapılar