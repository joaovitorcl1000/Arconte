import json
import panphon
from panphon.featuretable import FeatureTable

def build_ipa_matrix(output_path: str = "ipa_matrix.json"):
    ft = FeatureTable()
    
    # Segmentos conhecidos catalogados pelo modelo fonológico do panphon
    all_segments = ft.all_ipa_segments()
    
    matrix = []
    
    for seg in sorted(all_segments):
        # Obtém o dicionário de traços binários (+1, -1, 0)
        features = ft.word_to_feature_dict(seg)
        if not features:
            continue
        
        feat = features[0]
        
        # Classificação básica para filtros rápidos
        is_syl = feat.get("syl") == 1
        is_cons = feat.get("cons") == 1
        
        if is_syl and not is_cons:
            segment_type = "vowel"
        elif is_cons and not is_syl:
            segment_type = "consonant"
        else:
            segment_type = "glide_or_syllabic_consonant"
            
        record = {
            "ipa": seg,
            "type": segment_type,
            "unicode_codepoints": [f"U+{ord(c):04X}" for c in seg],
            "features": feat
        }
        matrix.append(record)
        
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(matrix, f, ensure_ascii=False, indent=2)
        
    print(f"Sucesso! {len(matrix)} fones IPA válidos exportados para '{output_path}'.")

if __name__ == "__main__":
    build_ipa_matrix()
