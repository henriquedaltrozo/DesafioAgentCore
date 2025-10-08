from bedrock_agentcore import BedrockAgentCoreApp
import sys
import os

from src.analyzer import Analyzer
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from email_sender import EmailSender
import json
from datetime import datetime
import numpy as np
import pandas as pd
from dotenv import load_dotenv
import boto3

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
    bedrock_client = None

def make_json_serializable(obj):
    """Converte objetos para tipos serializáveis em JSON"""
    if isinstance(obj, dict):
        return {str(k): make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_serializable(v) for v in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
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
        system_prompt = """Você é um assistente especializado em análise de reclamações do Sicredi.

REGRAS IMPORTANTES:
1. Para saudações simples ("oi", "olá", "hello") - responda APENAS: "Oi! 👋 Posso te ajudar com análise das reclamações do Sicredi. O que você gostaria de saber?"
2. Para "que perguntas posso fazer" - liste exemplos práticos de perguntas organizados por categoria
3. NUNCA forneça dados automaticamente para saudações
4. Use os dados fornecidos para responder perguntas específicas

Seja útil, direto e sempre ofereça próximos passos."""
        
        context = ""
        if context_data:
            context = f"\n\nDados disponíveis: {json.dumps(context_data, indent=2, ensure_ascii=False)}"
        
        prompt = f"{system_prompt}\n\nPergunta do usuário: {user_message}{context}"
        
        if bedrock_client is None:
            raise Exception("Bedrock client is not available.")
        
        response = bedrock_client.invoke_model(
            modelId='amazon.nova-micro-v1:0',
            body=json.dumps({
                "messages": [{
                    "role": "user",
                    "content": [{"text": prompt}]
                }],
                "inferenceConfig": {
                    "max_new_tokens": 1000,
                    "temperature": 0.7
                }
            })
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['output']['message']['content'][0]['text']
        
    except Exception as e:
        return get_rule_based_response(user_message, context_data)

def get_rule_based_response(user_message, context_data=None):
    """Respostas baseadas em regras quando Bedrock não está disponível"""
    msg_lower = user_message.lower().strip()
    
    # Saudações simples - forçar resposta direta
    if msg_lower in ['oi', 'olá', 'hello', 'teste', 'bom dia', 'boa tarde']:
        return "Oi! 👋 Posso te ajudar com análise das reclamações do Sicredi. O que você gostaria de saber?"
    
    # Perguntas sobre funcionalidades
    if any(word in msg_lower for word in ['pode fazer', 'funcionalidade', 'capacidade', 'o que você', 'ajuda', 'perguntas posso', 'que perguntas']):
        return """💬 PERGUNTAS QUE VOCÊ PODE FAZER:

📊 SITUAÇÃO GERAL:
• "Qual a situação atual?"
• "Como estão as reclamações?"
• "Resumo geral"
• "Status das reclamações"

🎯 CATEGORIAS:
• "Qual categoria tem mais reclamações?"
• "Categoria mais problemática?"
• "Qual categoria tem menos problemas?"
• "Compare App vs Cartão"
• "Problemas do PIX"

📈 ANÁLISES:
• "Taxa de resolução"
• "Quantas foram resolvidas?"
• "Casos pendentes"
• "Tendências das reclamações"

💡 MELHORIAS:
• "Como melhorar o atendimento?"
• "Recomendações de melhoria"
• "Plano de ação"
• "Estratégias para resolver"

📋 RELATÓRIOS:
• "Gerar relatório"
• "Criar PDF"
• "Enviar para email@exemplo.com"
• "Análise completa"

🔍 ESPECÍFICAS:
• "Problemas do aplicativo"
• "Reclamações sobre cartão"
• "Como está o atendimento?"
• "Principais gargalos"

O que você gostaria de saber?"""

    # Perguntas específicas sobre situação/status
    if any(word in msg_lower for word in ['situação', 'status', 'como estão', 'situação atual', 'qual a situação']):
        if context_data and context_data.get('status'):
            status_data = context_data['status']
            total = context_data.get('total_reclamacoes', 0)
            resolvidas = status_data.get('Resolvido', {}).get('count', 0)
            taxa = (resolvidas / total * 100) if total > 0 else 0
            
            return f"""📊 SITUAÇÃO ATUAL DAS RECLAMAÇÕES:

📈 **NÚMEROS GERAIS:**
• Total de reclamações: {total}
• Resolvidas: {resolvidas} ({taxa:.1f}%)
• Pendentes: {total - resolvidas}

📋 **STATUS DETALHADO:**
{chr(10).join([f'• {status}: {data.get("count", 0)} casos' for status, data in status_data.items()])}

{'🚨 **ALERTA:** Taxa de resolução muito baixa!' if taxa < 50 else '✅ **BOM:** Taxa de resolução adequada!'} 

O que mais você gostaria saber?"""
        
    # Perguntas sobre categorias problemáticas
    if any(word in msg_lower for word in ['categoria', 'problemática', 'mais reclamações', 'quais categorias', 'categorias mais']):
        if context_data and context_data.get('categorias'):
            categorias = context_data['categorias']
            # Ordenar por quantidade de reclamações
            sorted_cats = sorted(categorias.items(), key=lambda x: x[1].get('count', 0), reverse=True)
            
            result = "🎯 CATEGORIAS MAIS PROBLEMÁTICAS:\n\n"
            for i, (cat, data) in enumerate(sorted_cats[:5]):
                emoji = "🔴" if i == 0 else "🟡" if i < 3 else "🟢"
                result += f"{emoji} **{cat}:** {data.get('count', 0)} reclamações\n"
            
            if sorted_cats:
                worst = sorted_cats[0]
                result += f"\n⚠️ **FOCO PRIORITÁRIO:** {worst[0]} precisa de atenção urgente!"
            
            result += "\n\nPrecisa de análise mais detalhada de alguma categoria?"
            return result
    
    # Perguntas sobre melhorias/recomendações
    if any(word in msg_lower for word in ['melhoria', 'recomendação', 'como melhorar', 'sugestão', 'plano', 'ação']):
        if context_data:
            return """💡 RECOMENDAÇÕES DE MELHORIA:

🎯 **AÇÕES IMEDIATAS:**
• Priorizar resolução de casos pendentes
• Implementar sistema de follow-up automático
• Criar SLA de 48h para primeira resposta

📊 **MELHORIAS DE PROCESSO:**
• Capacitar equipe nas categorias mais críticas
• Implementar chatbot para dúvidas simples
• Criar FAQ baseado em reclamações recorrentes

📈 **MONITORAMENTO:**
• Dashboard em tempo real
• Alertas automáticos para casos críticos
• Relatórios semanais de performance

🚀 **METAS:**
• Taxa de resolução >80% em 30 dias
• Tempo médio de resposta <24h
• Satisfação do cliente >4.5/5

Quer que eu gere um relatório detalhado com plano de ação específico?"""
        
    # Resposta padrão apenas se não foi uma pergunta específica
    if context_data:
        total = context_data.get('total_reclamacoes', 0)
        return f"Tenho {total} reclamações analisadas. Posso te ajudar com situação atual, categorias problemáticas, recomendações de melhoria ou gerar relatórios. O que você gostaria de saber?"
    return "Para começar, preciso analisar os dados. Digite 'analisar reclamações' para carregar as informações."

@app.entrypoint
def invoke(payload):
    """Agente de IA para análise inteligente de reclamações"""
    user_message = payload.get("prompt", "Analisar reclamações")
    recipient_email = payload.get("email", None)
    
    # Carregar dados para contexto da IA
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(os.path.dirname(current_dir), "data", "reclamacoes_20251001_220605.json")
    context_data = None
    
    if os.path.exists(json_file_path):
        analyzer = Analyzer(json_file_path)
        if analyzer.load_data():
            context_data = {
                "total_reclamacoes": analyzer.data['metadata']['total_reclamacoes'] if analyzer.data is not None else 0,
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
            is_analysis_request = True
    
    if not is_analysis_request:
        # Forçar fallback para saudações simples e perguntas sobre funcionalidades
        msg_lower = user_message.lower().strip()
        if msg_lower in ['oi', 'olá', 'hello', 'teste', 'bom dia', 'boa tarde']:
            return {
                "response": "Oi! 👋 Posso te ajudar com análise das reclamações do Sicredi. O que você gostaria de saber?",
                "status": "conversational",
                "context_available": context_data is not None
            }
        
        # Perguntas sobre funcionalidades - usar fallback
        if any(word in msg_lower for word in ['perguntas posso', 'que perguntas', 'pode fazer', 'funcionalidade']):
            return {
                "response": get_rule_based_response(user_message, context_data),
                "status": "conversational",
                "context_available": context_data is not None
            }
        
        # Resposta conversacional com IA para outras perguntas
        ai_response = get_ai_response(user_message, context_data)
        return {
            "response": ai_response,
            "status": "conversational",
            "context_available": context_data is not None
        }
    
    try:
        # Caminho para o arquivo JSON
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_file_path = os.path.join(os.path.dirname(current_dir), "data", "reclamacoes_20251001_220605.json")
        
        if not os.path.exists(json_file_path):
            return {
                "result": "Erro: Arquivo de reclamações não encontrado.",
                "status": "error"
            }
        
        analyzer = Analyzer(json_file_path)
        
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
        
        if pdf_success:
            pdf_full_path = os.path.join(os.path.dirname(current_dir), "results", pdf_filename)
        
        # Obter estatísticas detalhadas
        categoria_analysis = analyzer.analyze_categories()
        status_analysis = analyzer.analyze_status() or {}
        trends = analyzer.analyze_trends()
        
        # Converter trends para formato JSON serializável
        trends_serializable = {
            'date_range': trends['date_range'] if trends and 'date_range' in trends else {},
            'daily_trends_count': len(trends['daily_trends']) if trends and hasattr(trends['daily_trends'], '__len__') else 0,
            'weekly_trends_summary': {str(k): int(v) for k, v in trends['weekly_trends'].items()} if trends and hasattr(trends['weekly_trends'], 'items') else {}
        }
        
        result = {
            "summary": summary,
            "categoria_analysis": make_json_serializable(categoria_analysis),
            "status_analysis": make_json_serializable(status_analysis),
            "trends": trends_serializable,
            "pdf_generated": pdf_success,
            "pdf_filename": pdf_full_path if pdf_success else None,
            "status": "success"
        }
        
        # Gerar insights com IA
        resolvidos = status_analysis.get('Resolvido', {}).get('count', 0)
        total = sum(dados['count'] for dados in status_analysis.values())
        taxa_resolucao = (resolvidos / total) * 100
        
        # Gerar insights baseados nos dados
        categoria_critica = max(categoria_analysis.items(), key=lambda x: x[1]['count'])[0] if categoria_analysis else "N/A"
        nao_resolvidos = sum(dados['count'] for status, dados in status_analysis.items() if status != 'Resolvido')
        
        ai_insights = f"""🧠 INSIGHTS ESTRATÉGICOS GERADOS:

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

🚀 META: Elevar taxa de resolução para >80% em 30 dias"""
        
        result["ai_insights"] = ai_insights
        
        # Enviar por e-mail se solicitado
        if recipient_email:
            email_sender = EmailSender()
            email_result = email_sender.send_report_email(
                pdf_full_path if pdf_success else None,
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

if __name__ == "__main__":
    import sys
    email_destinatario = None
    
    if len(sys.argv) > 1:
        email_destinatario = sys.argv[1]
        print(f"E-mail de destino configurado: {email_destinatario}")
    
    payload = {"prompt": "Analisar reclamações e gerar relatório"}
    if email_destinatario:
        payload["email"] = email_destinatario
    
    result = invoke(payload)
    print("Análise concluída!")