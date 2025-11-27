from typing import Dict
from fastapi import FastAPI
from pydantic import BaseModel
from inference_engine import RecommendationEngine

app = FastAPI()

# Inicializa o motor UMA VEZ no escopo global
# Assim o pickle não precisa ser carregado a cada request (o que seria lento)
engine = RecommendationEngine()

class UserRequest(BaseModel):
    profile: Dict[str, int]

@app.post("/api/recommend")
def get_health_advice(user_req: UserRequest):
    # Converte o objeto Pydantic para dict
    user_data = user_req.profile
    
    # Chama nosso motor
    recommendations = engine.get_holistic_recommendations(user_data)
    
    return {"recommendations": recommendations}