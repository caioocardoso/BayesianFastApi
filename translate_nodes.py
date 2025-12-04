from deep_translator import GoogleTranslator

# 1. Dicionário de Termos Técnicos (Sua "Camada de Ouro" de tradução)
# Termos médicos/biohacking muitas vezes perdem o sentido no tradutor automático.
# Ex: "Grounding" vira "Fundamentação" ou "Castigo" no Google, mas você quer "Aterramento".
SPECIAL_TERMS = {
    "grounding": "aterramento",
    "training": "treino",
    "workout": "exercício",
    "exercise": "exercício",  # ← ADICIONAR
    "gut": "intestino",
    "sleep": "sono",
    "aging": "envelhecimento",
    "dysbiosis": "disbiose",
    "direct relation": "relação direta",  # ← ADICIONAR
}

def translate_nodes(recommendations):
    translator = GoogleTranslator(source='en', target='pt')
    translated_recs = []
    
    for rec in recommendations:
        translated_rec = {}
        
        # Traduz cada campo
        for key, value in rec.items():
            if isinstance(value, str):
                # Verifica primeiro no dicionário (case-insensitive)
                value_lower = value.lower()
                if value_lower in SPECIAL_TERMS:
                    translated_rec[key] = SPECIAL_TERMS[value_lower]
                else:
                    try:
                        translated_rec[key] = translator.translate(value)
                    except:
                        translated_rec[key] = value  # Mantém original se falhar
            else:
                translated_rec[key] = value
        
        translated_recs.append(translated_rec)
    
    return translated_recs