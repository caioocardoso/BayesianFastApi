import pickle
import networkx as nx

class RecommendationEngine:
    def __init__(self, model_path="bayesian_network_model.pkl"):
        print(f"Carregando topologia de: {model_path}...")
        try:
            with open(model_path, "rb") as f:
                self.model = pickle.load(f)
            # Não carregamos mais VariableElimination (pesado). 
            # Só precisamos do grafo.
            self.all_nodes = set(self.model.nodes())
            print(f"Grafo carregado! Nós: {len(self.all_nodes)}")
        except Exception as e:
            print(f"ERRO CRÍTICO: {e}")
            self.model = None

    def get_holistic_recommendations(self, user_profile):
        """
        Lógica Simplificada:
        1. Olha o que está ruim (valor 0).
        2. Olha no grafo quem causa isso (Predecessores/Pais).
        3. Recomenda os pais.
        """
        if not self.model:
            return []

        recommendations = []
        
        # 1. Identificar "Dores" (Targets)
        # O user_profile deve vir com chaves em Inglês (ex: "sleep", "exercise")
        targets_to_improve = []
        
        # Guardamos o que o usuário já faz bem para não recomendar o óbvio
        # Ex: Se ele já faz exercício, não recomende exercício só porque melhora o sono.
        current_habits = set()

        for key, value in user_profile.items():
            if key in self.all_nodes:
                if value == 0: 
                    targets_to_improve.append(key)
                elif value == 1:
                    current_habits.add(key)
        
        print(f"🔍 Buscando causas para: {targets_to_improve}")

        # 2. Varredura Topológica (Pais Imediatos)
        for target in targets_to_improve:
            # Em grafos direcionados, 'predecessors' são os nós que apontam PARA o target.
            # Causa -> Efeito. Logo, pegamos as Causas.
            causes = list(self.model.predecessors(target))
            
            for habit in causes:
                # Filtragem básica:
                # 1. Não recomendar o que ele já faz (current_habits)
                # 2. Não recomendar o próprio alvo (loop)
                if habit not in current_habits and habit != target:
                    
                    # Adiciona recomendação
                    recommendations.append({
                        "area_focus": target,       # "Melhorar: sleep"
                        "suggested_habit": habit,   # "Causa encontrada: exercise"
                        "type": "Direct Relation"   # Apenas informativo
                    })

        return recommendations