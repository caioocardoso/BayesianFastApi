from deep_translator import GoogleTranslator

# 1. Dicionário de Termos Técnicos (Sua "Camada de Ouro" de tradução)
# Termos médicos/biohacking muitas vezes perdem o sentido no tradutor automático.
# Ex: "Grounding" vira "Fundamentação" ou "Castigo" no Google, mas você quer "Aterramento".
SPECIAL_TERMS = {
    "grounding": "aterramento",
    "training": "treino",
    "workout": "exercício",
    "gut": "intestino",
    "sleep": "sono",
    "aging": "envelhecimento",
    "dysbiosis": "disbiose"
}

def translate_nodes(recommendations):
    translator = GoogleTranslator(source='en', target='pt')
    
    for rec in recommendations:
        # Traduz os campos individuais
        if rec["area_focus"] in SPECIAL_TERMS:
            rec["area_focus"] = SPECIAL_TERMS[rec["area_focus"]]
        else:
            try:
                rec["area_focus"] = translator.translate(rec["area_focus"])
            except:
                pass
                
        if rec["suggested_habit"] in SPECIAL_TERMS:
            rec["suggested_habit"] = SPECIAL_TERMS[rec["suggested_habit"]]
        else:
            try:
                rec["suggested_habit"] = translator.translate(rec["suggested_habit"])
            except:
                pass
    
    return recommendations