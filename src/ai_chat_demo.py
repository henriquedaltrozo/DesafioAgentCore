#!/usr/bin/env python3
"""
🤖 Demo do Agente de IA Conversacional
Demonstra como usar o Bedrock AgentCore como verdadeira IA
"""

from my_agent import app, invoke
import json

def demo_conversational_ai():
    """Demonstra capacidades conversacionais do agente"""
    
    print("🤖 AGENTE IA CONVERSACIONAL - SICREDI")
    print("=" * 50)
    print("Digite suas perguntas ou 'sair' para encerrar")
    print("Exemplos:")
    print("- Qual a categoria com mais reclamações?")
    print("- Como melhorar o serviço?")
    print("- Analisar reclamações (para gerar relatório)")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("\n💬 Você: ").strip()
            
            if user_input.lower() in ['sair', 'exit', 'quit']:
                print("👋 Até logo!")
                break
                
            if not user_input:
                continue
            
            # Chamar o agente de IA
            payload = {"prompt": user_input}
            print("\n🔄 Processando...")
            response = invoke(payload)
            
            if response.get('status') == 'conversational':
                print(f"\n🤖 Agente IA: {response.get('response')}")
            elif response.get('status') == 'success':
                print(f"\n🤖 Agente IA: {response.get('ai_insights', 'Análise concluída!')}")
            else:
                print(f"\n❌ Erro: {response.get('result', 'Erro desconhecido')}")
            
            # Se foi gerado relatório, mostrar detalhes
            if response.get('status') == 'success' and response.get('pdf_generated'):
                print(f"\n📊 Relatório gerado: {response.get('pdf_filename')}")
                
                # Status do email
                if response.get("email_sent"):
                    print(f"\n✅ E-mail enviado com sucesso!")
                elif 'email_message' in response:
                    print(f"\n❌ Erro no e-mail: {response.get('email_message')}")
                
        except KeyboardInterrupt:
            print("\n👋 Encerrando...")
            break
        except Exception as e:
            print(f"\n❌ Erro: {e}")

def demo_api_calls():
    """Demonstra chamadas diretas da API"""
    
    print("\n🔧 DEMO - CHAMADAS DIRETAS DA API")
    print("=" * 40)
    
    # Exemplos de perguntas conversacionais
    perguntas = [
        "Qual é a situação atual das reclamações?",
        "Quais são os principais problemas identificados?",
        "Como posso melhorar o atendimento ao cliente?",
        "Analisar reclamações e gerar relatório"
    ]
    
    for pergunta in perguntas:
        print(f"\n📝 Pergunta: {pergunta}")
        
        payload = {"prompt": pergunta}
        response = invoke(payload)
        
        if response.get('status') == 'conversational':
            print(f"🤖 Resposta IA: {response.get('response')}")
        elif response.get('status') == 'success':
            print("📊 Análise completa gerada!")
            print(f"   • PDF: {response.get('pdf_filename')}")
            print(f"   • Insights: {response.get('ai_insights', 'N/A')[:100]}...")
            if response.get("email_sent"):
                print(f"   • E-mail: Enviado com sucesso")
            elif 'email_message' in response:
                print(f"   • E-mail: Erro - {response.get('email_message')[:50]}...")
        else:
            print(f"❌ Erro: {response.get('result')}")
        
        print("-" * 40)

if __name__ == "__main__":
    print("Escolha o modo de demonstração:")
    print("1. Chat interativo")
    print("2. Chamadas de API")
    
    escolha = input("Digite 1 ou 2: ").strip()
    
    if escolha == "1":
        demo_conversational_ai()
    elif escolha == "2":
        demo_api_calls()
    else:
        print("Opção inválida. Executando chat interativo...")
        demo_conversational_ai()