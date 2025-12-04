from fastapi import FastAPI
from pydantic import BaseModel
from inference_engine import RecommendationEngine
from translate_nodes import translate_nodes

app = FastAPI()

# Inicializa o motor UMA VEZ no escopo global
# Assim o pickle não precisa ser carregado a cada request (o que seria lento)
engine = RecommendationEngine()

class UserRequest(BaseModel):
    profile: dict[str, int]

@app.post("/api/recommend")
def get_health_advice(user_req: UserRequest):
    # Converte o objeto Pydantic para dict
    user_data = user_req.profile
    
    # Chama nosso motor
    recommendations = engine.get_holistic_recommendations(user_data)
    
    recommendations_translated = translate_nodes(recommendations)
    
    return {"recommendations": recommendations_translated}