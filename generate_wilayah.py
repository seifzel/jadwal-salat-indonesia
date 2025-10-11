import os
import json
import re

# Folder tempat file JSON berada
DATA_FOLDER = "data"
OUTPUT_FILE = "wilayah.json"

# Pola nama file yang diharapkan:
# Contoh: "ACEH KAB. ACEH SELATAN 10 2025.json"
pattern = re.compile(r"^([A-Z .']+?) (KAB\.|KOTA) ([A-Z .']+) 10 2025\.json$", re.IGNORECASE)

wilayah = {}

for file in os.listdir(DATA_FOLDER):
    if not file.endswith(".json"):
        continue

    match = pattern.match(file.replace("_", " "))
    if not match:
        print(f"⚠️ Lewati file (tidak cocok pola): {file}")
        continue

    provinsi = match.group(1).strip().upper()
    tipe = match.group(2).strip().upper()
    nama = match.group(3).strip().upper()

    nama_final = f"{tipe} {nama}"

    if provinsi not in wilayah:
        wilayah[provinsi] = []

    if nama_final not in wilayah[provinsi]:
        wilayah[provinsi].append(nama_final)

# Urutkan provinsi dan kabupaten agar rapi
for prov in wilayah:
    wilayah[prov].sort()
wilayah = dict(sorted(wilayah.items()))

# Simpan ke file JSON
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(wilayah, f, ensure_ascii=False, indent=4)

print(f"✅ File '{OUTPUT_FILE}' berhasil dibuat ({len(wilayah)} provinsi)")
