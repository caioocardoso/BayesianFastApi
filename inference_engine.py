import pickle
import pandas as pd
from pgmpy.inference import VariableElimination

class RecommendationEngine:
    def __init__(self, model_path="bayesian_network_model.pkl"):
        """
        Carrega o modelo salvo e prepara o motor de inferência.
        Isso deve rodar apenas UMA vez quando a API inicia.
        """
        print(f"Carregando modelo de: {model_path}...")
        try:
            with open(model_path, "rb") as f:
                self.model = pickle.load(f)
            
            # Validação básica para garantir que o modelo está ok
            if not hasattr(self.model, 'nodes'):
                raise Exception("O arquivo não contém um modelo válido.")
                
            # Inicializa o algoritmo de eliminação de variáveis (o cérebro matemático)
            self.infer = VariableElimination(self.model)
            print("Modelo carregado e motor de inferência pronto!")
            
            # Lista de nós disponíveis para consulta (debug)
            print(f"Nós disponíveis: {self.model.nodes()}")
            
        except Exception as e:
            print(f"Erro crítico ao carregar modelo: {e}")
            self.model = None

    def predict_impact(self, current_evidence, target_variable, intervention_variable, desired_state=1):
        """
        Calcula o impacto de mudar UM hábito específico.
        
        Args:
            current_evidence (dict): O estado atual do usuário (ex: {'stress': 1})
            target_variable (str): O que queremos melhorar (ex: 'sleep')
            intervention_variable (str): O hábito a ser mudado (ex: 'exercise')
            desired_state (int): O estado "ideal" do hábito (1 = Bom/Presente)
        
        Returns:
            float: A diferença de probabilidade (Impacto).
        """
        if self.model is None: return 0.0

        # 1. Probabilidade Base: Como o usuário está HOJE?
        # Removemos o hábito que vamos testar da evidência atual para não enviesar
        base_evidence = {k:v for k,v in current_evidence.items() if k != intervention_variable}
        
        try:
            base_prob_dist = self.infer.query([target_variable], evidence=base_evidence)
            # Pegamos a probabilidade do estado 1 (Bom/Melhorado)
            base_prob = base_prob_dist.values[1] 
        except:
            # Se der erro (ex: evidência impossível), retorna 0
            return 0.0

        # 2. Probabilidade Simulada: E se o usuário adotar o hábito?
        simulated_evidence = base_evidence.copy()
        simulated_evidence[intervention_variable] = desired_state # Força o hábito para "Bom"
        
        try:
            new_prob_dist = self.infer.query([target_variable], evidence=simulated_evidence)
            new_prob = new_prob_dist.values[1]
        except:
            return 0.0

        # 3. O Impacto é a diferença
        impact = new_prob - base_prob
        return impact

    def get_recommendations(self, user_responses):
        """
        Gera a lista final de recomendações ordenadas.
        """
        # Mapeia as respostas do formulário para os nomes EXATOS dos nós da sua rede
        # (Você precisa ajustar isso baseados nos nós que vi no seu arquivo pkl)
        evidence = {}
        
        # Exemplo de mapeamento (ajuste conforme seu formulário Android)
        # Se o usuário disse que come mal, entra como 0. Se come bem, 1.
        if 'frutas_vegetais' in user_responses:
            evidence['fruit and vegetable intake'] = user_responses['frutas_vegetais'] # 0 ou 1
        if 'exercicio' in user_responses:
            evidence['exercise'] = user_responses['exercicio']
        
        # O objetivo é melhorar o Sono? Ou a Saúde Subjetiva?
        target = 'sleep' 
        
        # Lista de hábitos que seu app pode sugerir (devem existir no grafo)
        # Baseado no seu arquivo, vi estes nomes:
        possible_interventions = [
            'exercise', 
            'fruit and vegetable intake', 
            'upf consumption', # Consumo de ultraprocessados
            'alcohol consumption'
        ]
        
        recommendations = []
        
        for habit in possible_interventions:
            # Se o usuário já faz isso bem (estado 1), não precisa recomendar
            if evidence.get(habit) == 1:
                continue
                
            # Calcula impacto
            impact = self.predict_impact(evidence, target, habit)
            
            if impact > 0.01: # Só recomenda se tiver impacto real (> 1%)
                recommendations.append({
                    "habit": habit,
                    "score": round(impact * 100, 1), # Transformando em porcentagem
                    "message": f"Melhorar '{habit}' pode aumentar sua qualidade de sono em {round(impact*100)}%."
                })
        
        # Ordena do maior impacto para o menor
        return sorted(recommendations, key=lambda x: x['score'], reverse=True)

# --- Exemplo de Uso (Teste Local) ---
if __name__ == "__main__":
    # Simula o servidor iniciando
    engine = RecommendationEngine("bayesian_network_model.pkl")
    
    # Simula um usuário vindo do Android
    # Ele não faz exercício (0) e come mal (0)
    fake_user_data = {
        'exercicio': 0, 
        'frutas_vegetais': 0
    }
    
    recs = engine.get_recommendations(fake_user_data)
    
    print("\n--- Recomendações para o Usuário ---")
    for r in recs:
        print(f"Hábito: {r['habit']} | Impacto: +{r['score']}% | {r['message']}")