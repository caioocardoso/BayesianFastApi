from fastapi import FastAPI
from pydantic import BaseModel
from inference_engine import RecommendationEngine

app = FastAPI()

# Inicializa o motor UMA VEZ no escopo global
# Assim o pickle não precisa ser carregado a cada request (o que seria lento)
engine = RecommendationEngine()

class UserProfile(BaseModel):
    exercicio: int # 0 ou 1
    frutas_vegetais: int

@app.post("/api/recommend")
def get_health_advice(profile: UserProfile):
    # Converte o objeto Pydantic para dict
    user_data = profile.dict()
    
    # Chama nosso motor
    recommendations = engine.get_recommendations(user_data)
    
    return {"recommendations": recommendations}