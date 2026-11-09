import pandas as pd
import json

df = pd.read_csv("phoible.csv", low_memory=False)

# Pega os segmentos únicos e as colunas de traços fonéticos
feature_cols = [c for c in df.columns if c.startswith("feature_") or c in [
    "Phoneme", "SegmentClass", "tone", "stress", "syllabic", "consonantal", 
    "sonorant", "continuant", "delayedRelease", "voice", "nasal"
]]

unique_phonemes = df[["Phoneme", "SegmentClass"]].drop_duplicates().dropna()

phonemes_list = unique_phonemes.to_dict(orient="records")
with open("phoible_inventory.json", "w", encoding="utf-8") as f:
    json.dump(phonemes_list, f, ensure_ascii=False, indent=2)

print(f"Exportados {len(phonemes_list)} fonemas atestados da humanidade.")
