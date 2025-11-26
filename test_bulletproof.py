import pickle
import requests
import json
import networkx as nx
import random

# CONFIGURAÇÃO
MODEL_PATH = "bayesian_network_model.pkl"
API_URL = "http://127.0.0.1:8000/api/recommend"

def find_valid_test_scenario():
    """
    Abre o modelo e procura UMA conexão real (Causa -> Efeito) para testar.
    Não adivinhamos nada. Lemos a topologia real.
    """
    try:
        print(f"🔍 Inspecionando o modelo: {MODEL_PATH}...")
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
            
        # Procura um nó que tenha pelo menos um "Pai" (Predecessor)
        valid_scenarios = []
        for node in model.nodes():
            parents = list(model.predecessors(node))
            if parents:
                # Encontramos um alvo (node) e uma causa (parent)
                valid_scenarios.append((node, parents[0]))
        
        if not valid_scenarios:
            print("❌ FATAL: Seu modelo é um 'Grafo Desconectado'. Não existem setas ligando nada a nada.")
            print("   O Inference Engine nunca vai recomendar nada porque não existem causas.")
            return None, None
            
        # Escolhe um cenário aleatório para testar
        target, cause = random.choice(valid_scenarios)
        print(f"✅ Cenário de Teste Encontrado: '{cause}' afeta '{target}'")
        return target, cause

    except Exception as e:
        print(f"❌ Erro ao ler o pickle: {e}")
        return None, None

def run_test():
    # 1. Descobrir o que testar
    target_node, cause_node = find_valid_test_scenario()
    
    if not target_node:
        return # Aborta se o modelo estiver quebrado

    # 2. Montar o Payload "Matador"
    # Dizemos que o Alvo está ruim (0) e a Causa está ruim (0)
    # O sistema DEVE recomendar a Causa.
    payload = {
        "profile": {
            target_node: 0, # O problema (ex: Sono ruim)
            cause_node: 0,  # A oportunidade (ex: Sem exercício)
            "dummy_variable": 1 # Só pra encher linguiça
        }
    }

    print(f"🚀 Enviando Payload Dinâmico: {json.dumps(payload, indent=2)}")

    # 3. Disparar contra a API
    try:
        response = requests.post(API_URL, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            recs = data.get("recommendations", [])
            
            # 4. A Prova dos Nove
            found = False
            print("\n📋 Resposta da API:")
            for rec in recs:
                print(f"   - Recomendou: {rec['suggested_habit']} (para melhorar {rec['area_focus']})")
                if rec['suggested_habit'] == cause_node and rec['area_focus'] == target_node:
                    found = True
            
            print("-" * 30)
            if found:
                print(f"🏆 SUCESSO ABSOLUTO! O sistema detectou corretamente que '{cause_node}' ajuda em '{target_node}'.")
                print("   Seu backend está pronto para o Frontend.")
            else:
                print(f"⚠️ ALERTA: A conexão existe no grafo, mas a API não recomendou.")
                print("   Verifique se o seu loop no 'inference_engine.py' está filtrando algo indevidamente.")
                
        else:
            print(f"❌ Erro na API: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"❌ Erro de conexão com a API: {e}")

if __name__ == "__main__":
    run_test()