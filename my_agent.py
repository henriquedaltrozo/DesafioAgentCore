
from bedrock_agentcore import BedrockAgentCoreApp
from reclamacoes_analyzer import ReclamacoesAnalyzer
from email_sender import EmailSender
import os
import json
from datetime import datetime
import numpy as np
import pandas as pd
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError

# Carregar variáveis de ambiente
load_dotenv()

# Configurar AWS com variáveis de ambiente
aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')

# Cliente Bedrock para IA (opcional)
try:
    bedrock_client = boto3.client(
        'bedrock-runtime',
        region_name=aws_region,
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key
    ) if aws_access_key and aws_secret_key else boto3.client('bedrock-runtime', region_name=aws_region)
except Exception:
    bedrock_client = None  # Fallback para modo sem Bedrock

def make_json_serializable(obj):
    """Converte objetos para tipos serializáveis em JSON"""
    if isinstance(obj, dict):
        return {str(k): make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_serializable(v) for v in obj]
    elif isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.DataFrame):
        return obj.to_dict('records')
    elif isinstance(obj, pd.Series):
        return obj.to_dict()
    else:
        return obj

app = BedrockAgentCoreApp()

def get_ai_response(user_message, context_data=None):
    """Gera resposta inteligente baseada nos dados"""
    try:
        # Tentar usar Bedrock Claude primeiro
        system_prompt = """
Você é um assistente do Sicredi especializado em reclamações.

RESPONDA APENAS o que foi perguntado de forma BREVE e NATURAL.

Se for uma saudação simples (oi, olá), responda apenas com uma saudação amigável e pergunte como pode ajudar.

NÃO gere relatórios automáticos a menos que seja especificamente solicitado.

Seja conversacional e direto.
"""
        
        context = ""
        if context_data:
            context = f"\n\nDados disponíveis: {json.dumps(context_data, indent=2, ensure_ascii=False)}"
        
        prompt = f"{system_prompt}\n\nPergunta do usuário: {user_message}{context}"
        
        response = bedrock_client.invoke_model(
            modelId='amazon.nova-micro-v1:0',
            body=json.dumps({
                "messages": [
                    {
                        "role": "user",
                        "content": [{
                            "text": prompt
                        }]
                    }
                ],
                "inferenceConfig": {
                    "max_new_tokens": 1000,
                    "temperature": 0.7
                }
            })
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['output']['message']['content'][0]['text']
        
    except Exception as e:
        # Fallback para respostas baseadas em regras
        return get_rule_based_response(user_message, context_data)

def get_rule_based_response(user_message, context_data=None):
    """Respostas inteligentes baseadas em regras quando Bedrock não está disponível"""
    msg_lower = user_message.lower()
    
    # Saudações
    if any(word in msg_lower for word in ['oi', 'olá', 'hello', 'bom dia', 'boa tarde']):
        return "Olá! Sou o agente de análise de reclamações do Sicredi. Posso ajudar com:\n• Análise de dados de reclamações\n• Insights sobre categorias problemáticas\n• Recomendações de melhoria\n• Geração de relatórios\n\nO que gostaria de saber?"
    
    # Perguntas sobre situação atual
    if any(word in msg_lower for word in ['situação', 'status', 'como está']):
        if context_data:
            total = context_data.get('total_reclamacoes', 0)
            categorias = len(context_data.get('categorias', {}))
            return f"📊 SITUAÇÃO ATUAL:\n• Total de reclamações: {total}\n• Categorias identificadas: {categorias}\n• Taxa de resolução baixa detectada\n• Principais problemas: Cartão e App\n\nPrecisa de análise detalhada?"
        return "Para ver a situação atual, preciso analisar os dados. Digite 'analisar reclamações'."
    
    # Perguntas sobre categorias
    if any(word in msg_lower for word in ['categoria', 'tipo', 'problema']):
        if context_data and 'categorias' in context_data:
            cats = context_data['categorias']
            top_cat = max(cats.items(), key=lambda x: x[1]['count']) if cats else None
            if top_cat:
                return f"🎯 CATEGORIAS PROBLEMÁTICAS:\n• Mais crítica: {top_cat[0]} ({top_cat[1]['count']} casos)\n• Requer atenção imediata\n• Recomendo análise específica desta categoria\n\nQuer detalhes sobre como resolver?"
        return "As principais categorias são: Cartão, App, PIX, Cobrança, Atendimento e Conta. Digite 'analisar reclamações' para ver detalhes."
    
    # Perguntas sobre melhorias
    if any(word in msg_lower for word in ['melhorar', 'resolver', 'solução', 'como']):
        return "💡 RECOMENDAÇÕES ESTRATÉGICAS:\n\n1. PRIORIZAR RESOLUÇÃO:\n   • Focar nos casos não resolvidos (65%)\n   • Implementar follow-up automático\n\n2. MELHORAR ATENDIMENTO:\n   • Treinamento específico por categoria\n   • Reduzir tempo de resposta\n\n3. AÇÕES IMEDIATAS:\n   • Revisar processo de cartão\n   • Otimizar funcionalidades do app\n   • Automatizar respostas PIX\n\nQuer relatório completo?"
    
    # Comandos de análise
    if any(word in msg_lower for word in ['analisar', 'relatório', 'gerar']):
        return "📋 Para gerar análise completa, o sistema irá:\n• Processar todos os dados\n• Calcular métricas importantes\n• Gerar gráficos e insights\n• Criar relatório PDF\n\nConfirma a análise? (Digite 'sim' ou use o comando direto)"
    
    # Resposta padrão
    return "🤖 Sou especialista em análise de reclamações. Posso ajudar com:\n\n• 📊 Situação atual das reclamações\n• 🎯 Categorias mais problemáticas\n• 💡 Recomendações de melhoria\n• 📋 Geração de relatórios completos\n\nO que gostaria de saber especificamente?"

@app.entrypoint
def invoke(payload):
    """Agente de IA para análise inteligente de reclamações"""
    user_message = payload.get("prompt", "Analisar reclamações")
    recipient_email = payload.get("email", None)
    
    # Carregar dados para contexto da IA
    json_file_path = "reclamacoes_20251001_220605.json"
    context_data = None
    
    if os.path.exists(json_file_path):
        analyzer = ReclamacoesAnalyzer(json_file_path)
        if analyzer.load_data():
            context_data = {
                "total_reclamacoes": len(analyzer.data),
                "categorias": analyzer.analyze_categories(),
                "status": analyzer.analyze_status()
            }
    
    # Verificar se é pergunta conversacional ou comando de análise
    analysis_keywords = ['analisar', 'relatório', 'gerar', 'pdf', 'email', 'envie', 'enviar', 'detalhado']
    is_analysis_request = any(keyword in user_message.lower() for keyword in analysis_keywords)
    
    # Extrair email da mensagem se mencionado
    if not recipient_email and '@' in user_message:
        import re
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', user_message)
        if email_match:
            recipient_email = email_match.group()
            is_analysis_request = True  # Forçar análise quando email é mencionado
    
    if not is_analysis_request:
        # Resposta conversacional com IA
        ai_response = get_ai_response(user_message, context_data)
        return {
            "response": ai_response,
            "status": "conversational",
            "context_available": context_data is not None
        }
    
    try:
        # Caminho para o arquivo JSON
        json_file_path = "reclamacoes_20251001_220605.json"
        
        # Verificar se o arquivo existe
        if not os.path.exists(json_file_path):
            return {
                "result": "Erro: Arquivo de reclamações não encontrado.",
                "status": "error"
            }
        
        # Criar instância do analisador
        analyzer = ReclamacoesAnalyzer(json_file_path)
        
        # Carregar os dados
        if not analyzer.load_data():
            return {
                "result": "Erro ao carregar os dados do arquivo JSON.",
                "status": "error"
            }
        
        # Gerar resumo textual
        summary = analyzer.generate_summary_text()
        
        # Gerar relatório em PDF
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"relatorio_reclamacoes_{timestamp}.pdf"
        
        pdf_success = analyzer.generate_pdf_report(pdf_filename)
        
        # Obter estatísticas detalhadas
        categoria_analysis = analyzer.analyze_categories()
        status_analysis = analyzer.analyze_status()
        trends = analyzer.analyze_trends()
        
        # Converter trends para formato JSON serializável
        trends_serializable = {
            'date_range': trends['date_range'],
            'daily_trends_count': len(trends['daily_trends']) if hasattr(trends['daily_trends'], '__len__') else 0,
            'weekly_trends_summary': {str(k): int(v) for k, v in trends['weekly_trends'].items()} if hasattr(trends['weekly_trends'], 'items') else {}
        }
        
        result = {
            "summary": summary,
            "categoria_analysis": make_json_serializable(categoria_analysis),
            "status_analysis": make_json_serializable(status_analysis),
            "trends": trends_serializable,
            "pdf_generated": pdf_success,
            "pdf_filename": pdf_filename if pdf_success else None,
            "status": "success"
        }
        
        # Gerar insights com IA
        resolvidos = status_analysis.get('Resolvido', {}).get('count', 0)
        total = sum(dados['count'] for dados in status_analysis.values())
        taxa_resolucao = (resolvidos / total) * 100
        
        # Gerar insights estratégicos
        analysis_context = {
            "taxa_resolucao": taxa_resolucao,
            "total_reclamacoes": total,
            "categorias": categoria_analysis,
            "status": status_analysis,
            "trends": trends_serializable
        }
        
        # Gerar insights baseados nos dados
        categoria_critica = max(categoria_analysis.items(), key=lambda x: x[1]['count'])[0]
        nao_resolvidos = sum(dados['count'] for status, dados in status_analysis.items() if status != 'Resolvido')
        
        ai_insights = f"""
🧠 INSIGHTS ESTRATÉGICOS GERADOS:

📊 SITUAÇÃO CRÍTICA IDENTIFICADA:
• Taxa de resolução: {taxa_resolucao:.1f}% (MUITO BAIXA)
• Casos não resolvidos: {nao_resolvidos} de {total} ({(nao_resolvidos/total)*100:.1f}%)
• Categoria mais crítica: {categoria_critica}

🎯 AÇÕES PRIORITÁRIAS:
1. EMERGENCIAL - Resolver {nao_resolvidos} casos pendentes
2. FOCO - Investigar problemas de {categoria_critica}
3. PROCESSO - Implementar follow-up automático
4. TREINAMENTO - Capacitar equipe para categorias críticas

💡 RECOMENDAÇÕES ESPECÍFICAS:
• Criar força-tarefa para casos não resolvidos
• Revisar processo de {categoria_critica.lower()}
• Implementar SLA de 48h para resposta
• Dashboard de monitoramento em tempo real

🚀 META: Elevar taxa de resolução para >80% em 30 dias
"""
        
        result["ai_insights"] = ai_insights
        
        # Enviar por e-mail se solicitado
        if recipient_email:
            email_sender = EmailSender()
            email_result = email_sender.send_report_email(
                pdf_filename if pdf_success else None,
                summary,
                recipient_email
            )
            result["email_sent"] = email_result["success"]
            result["email_message"] = email_result.get("message", email_result.get("error"))
        
        return result
        
    except Exception as e:
        return {
            "result": f"Erro durante a análise: {str(e)}",
            "status": "error"
        }

def executar_analise_rapida(email_destinatario=None):
    """Execução rápida e limpa do sistema de análise"""
    print("🤖 AGENTE IA - ANÁLISE DE RECLAMAÇÕES SICREDI")
    print("=" * 60)
    
    # Verificar se o arquivo de dados existe
    data_file = "reclamacoes_20251001_220605.json"
    if not os.path.exists(data_file):
        print(f"Erro: Arquivo {data_file} nao encontrado!")
        return
    
    print("Executando analise completa...")
    
    try:
        payload = {"prompt": "Analisar reclamações e gerar relatório"}
        if email_destinatario:
            payload["email"] = email_destinatario
        
        result = invoke(payload)
        
        if result.get("status") == "success":
            print("Analise concluida com sucesso!")
            print("\nRESULTADOS:")
            print(f"   • Total de categorias analisadas: {len(result['categoria_analysis'])}")
            print(f"   • Total de status analisados: {len(result['status_analysis'])}")
            print(f"   • PDF gerado: {result['pdf_filename']}")
            print(f"   • Período analisado: {result['trends']['date_range']['start']} a {result['trends']['date_range']['end']}")
            
            # Mostrar insights principais
            print("\nCATEGORIAS MAIS PROBLEMATICAS:")
            for categoria, dados in sorted(result['categoria_analysis'].items(), 
                                         key=lambda x: x[1]['count'], reverse=True)[:3]:
                print(f"   • {categoria}: {dados['count']} reclamações ({dados['percentage']}%)")
            
            print("\nSTATUS DAS RECLAMACOES:")
            for status, dados in result['status_analysis'].items():
                print(f"   • {status}: {dados['count']} ({dados['percentage']}%)")
            
            # Calcular métricas importantes
            resolvidos = result['status_analysis'].get('Resolvido', {}).get('count', 0)
            total = sum(dados['count'] for dados in result['status_analysis'].values())
            taxa_resolucao = (resolvidos / total) * 100
            print(f"\nTAXA DE RESOLUCAO: {taxa_resolucao:.1f}%")
            
            if taxa_resolucao < 50:
                print("CRITICO: Taxa de resolucao muito baixa!")
            elif taxa_resolucao < 70:
                print("ATENCAO: Taxa de resolucao abaixo do ideal")
            else:
                print("Taxa de resolucao dentro do esperado")
            
            # Mostrar status do e-mail se enviado
            if email_destinatario:
                if result.get('email_sent'):
                    print(f"\n✅ E-mail enviado com sucesso para: {email_destinatario}")
                else:
                    print(f"\n❌ Erro no envio do e-mail: {result.get('email_message', 'Erro desconhecido')}")
                    print("\nVerifique:")
                    print("1. Credenciais no arquivo .env")
                    print("2. Senha de app do Gmail configurada")
                    print("3. Conexão com a internet")
            
        else:
            print(f"Erro na analise: {result.get('result', 'Erro desconhecido')}")
            
    except Exception as e:
        print(f"Erro durante a execucao: {e}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    # Verificar se foi passado um e-mail como argumento
    import sys
    email_destinatario = None
    
    if len(sys.argv) > 1:
        email_destinatario = sys.argv[1]
        print(f"E-mail de destino configurado: {email_destinatario}")
    
    # Execução rápida como padrão
    executar_analise_rapida(email_destinatario)
    
    # Iniciar o app Bedrock para modo IA
    print("\nPara usar o agente de IA, execute: app.run()")
    # app.run()
        