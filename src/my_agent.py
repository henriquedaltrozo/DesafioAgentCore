
from bedrock_agentcore import BedrockAgentCoreApp
import sys
import os

from src.analyzer import Analyzer
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
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
        # Tentar usar Bedrock Claude primeiro
        system_prompt = """
Você é um assistente virtual especializado em analisar reclamações do Sicredi no site Reclame Aqui.  
Seu objetivo é conversar de forma natural, amigável e útil, transformando dados em insights claros e práticos.

🔹 ESTILO DE COMUNICAÇÃO
- Seja conversacional e fluido, evitando parecer um manual técnico.
- Traga explicações como se fosse uma pessoa próxima ajudando, não um robô.
- Use linguagem clara, frases corridas e só use listas curtas quando realmente organizar melhor a informação.
- Pode usar emojis com moderação para dar leveza.
- Sempre ofereça próximos passos: "Quer que eu detalhe isso em relatório?", "Prefere que eu envie por e-mail?", "Posso mostrar os dados em gráfico, se quiser."

🔹 O QUE VOCÊ CONSEGUE FAZER
1. **Situação geral**
   - Resumir o panorama atual das reclamações.
   - Mostrar taxa de resolução, principais categorias, evolução ao longo do tempo.

2. **Categorias**
   - Identificar categorias mais críticas ou com menos problemas.
   - Comparar categorias (ex: Cartão vs App).
   - Explicar tendências em categorias específicas.

3. **Status das reclamações**
   - Quantas foram resolvidas, pendentes, não respondidas.
   - Calcular taxa de resolução geral e por categoria.
   - Indicar onde estão os gargalos.

4. **Tendências e padrões**
   - Mostrar evolução das reclamações ao longo do tempo.
   - Identificar picos, sazonalidades ou quedas.
   - Destacar mudanças recentes que merecem atenção.

5. **Recomendações**
   - Sugerir ações práticas de melhoria (atendimento, processos, canais).
   - Propor metas realistas para aumentar a taxa de resolução.
   - Apontar oportunidades de aprendizado com categorias que já têm bons resultados.

6. **Relatórios**
   - Gerar relatório em PDF com gráficos e análises detalhadas.
   - Enviar relatório por e-mail, se solicitado.

🔹 COMO RESPONDER
- Quando pedirem situação geral → traga um resumo narrativo dos dados.
- Quando perguntarem por categorias → explique a mais problemática e a mais tranquila, de forma comparativa.
- Quando pedirem melhorias → sugira ações simples primeiro, depois estratégias mais avançadas.
- Quando falarem em relatório ou PDF → explique que pode gerar e/ou enviar por e-mail.
- Quando perguntarem “o que você pode fazer” → liste as principais capacidades de forma curta e simpática.
- Se não houver dados carregados → explique que precisa analisar primeiro e oriente o usuário.

🔹 TONS DE RESPOSTA (exemplos)
- Saudação: "Oi! 👋 Tudo bem? Posso te mostrar como estão as reclamações do Sicredi no Reclame Aqui ou preparar uma análise mais detalhada."
- Situação geral: "No momento temos X reclamações registradas. A categoria que mais preocupa é Y, enquanto Z é a mais tranquila. A taxa de resolução está em W%."
- Categoria: "A categoria mais crítica é Cartão, com N casos, já a de menor incidência é PIX, com apenas M."
- Melhoria: "Um bom caminho seria focar primeiro nos casos pendentes de Cartão, revisar o processo de atendimento e criar uma força-tarefa rápida. Quer que eu detalhe isso em um relatório?"
- Relatório: "Posso gerar um relatório completo com gráficos e insights. Quer que eu crie em PDF ou prefira que eu envie direto para o seu e-mail?"

Lembre-se: sempre soe como um analista próximo e colaborativo, e não como um chatbot genérico.
"""
        
        context = ""
        if context_data:
            context = f"\n\nDados disponíveis: {json.dumps(context_data, indent=2, ensure_ascii=False)}"
        
        prompt = f"{system_prompt}\n\nPergunta do usuário: {user_message}{context}"
        
        if bedrock_client is None:
            raise Exception("Bedrock client is not available.")
        
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
        return "Olá! Sou o agente de análise de reclamações do Sicredi. Posso ajudar com:\n\n📊 CONSULTAS:\n• Situação atual das reclamações\n• Categorias mais problemáticas\n• Status de resolução\n\n💡 ANÁLISES:\n• Insights e recomendações\n• Comparações entre categorias\n• Tendências e padrões\n\n📋 RELATÓRIOS:\n• Gerar análise completa em PDF\n• Enviar relatórios por email\n\nO que gostaria de saber?"
    
    # Resposta padrão
    if context_data:
        total = context_data.get('total_reclamacoes', 0)
        return f"🤖 Tenho {total} reclamações analisadas. Posso ajudar com:\n\n📊 CONSULTAS RÁPIDAS:\n• 'Situação atual' - Resumo geral\n• 'Categoria crítica' - Maior problema\n• 'Taxa de resolução' - Status atual\n\n💡 ANÁLISES AVANÇADAS:\n• 'Como melhorar?' - Recomendações\n• 'Gerar relatório' - PDF completo\n• 'Enviar para email@exemplo.com' - Relatório por email\n\nQual informação precisa?"
    return "🤖 Sistema de análise de reclamações. Digite 'analisar reclamações' para carregar os dados e começar a análise."
    
    # Perguntas sobre categorias - mais inteligente
    if any(word in msg_lower for word in ['categoria', 'tipo', 'problema']):
        if context_data and 'categorias' in context_data:
            cats = context_data['categorias']
            if cats:
                # Ordenar categorias por quantidade
                sorted_cats = sorted(cats.items(), key=lambda x: x[1]['count'], reverse=True)
                
                # Detectar se pergunta é sobre "mais" ou "menos"
                if any(word in msg_lower for word in ['menos', 'menor', 'baixa', 'mínimo', 'pequena']):
                    # Categoria com MENOS reclamações
                    bottom_cat = sorted_cats[-1]  # Último da lista (menor)
                    return f"📉 CATEGORIA COM MENOS RECLAMAÇÕES:\n• {bottom_cat[0]}: {bottom_cat[1]['count']} casos ({bottom_cat[1]['percentage']}%)\n• Esta categoria está com baixa incidência\n• Pode indicar processo bem estruturado\n"
                
                elif any(word in msg_lower for word in ['mais', 'maior', 'alta', 'máximo', 'crítica', 'problemática']):
                    # Categoria com MAIS reclamações  
                    top_cat = sorted_cats[0]  # Primeiro da lista (maior)
                    return f"🎯 CATEGORIA COM MAIS RECLAMAÇÕES:\n• {top_cat[0]}: {top_cat[1]['count']} casos ({top_cat[1]['percentage']}%)\n• Requer atenção imediata\n• Categoria mais problemática identificada\n"
                
                else:
                    # Pergunta geral sobre categorias
                    top_cat = sorted_cats[0]
                    return f"📊 RESUMO DAS CATEGORIAS:\n• Mais problemática: {top_cat[0]} ({top_cat[1]['count']} casos)\n• Total de categorias: {len(cats)}\n• Distribuição variada identificada\n"
                    
        return "As principais categorias são: Cartão, App, PIX, Cobrança, Atendimento e Conta. Digite 'analisar reclamações' para ver detalhes completos."
    
    # Perguntas sobre status das reclamações
    if any(word in msg_lower for word in ['resolvido', 'resolvida', 'status', 'pendente', 'respondida']):
        if context_data and 'status' in context_data:
            status_data = context_data['status']
            if status_data:
                sorted_status = sorted(status_data.items(), key=lambda x: x[1]['count'], reverse=True)
                
                if any(word in msg_lower for word in ['resolvido', 'resolvida', 'solucionado']):
                    resolvidos = status_data.get('Resolvido', {})
                    total = sum(s['count'] for s in status_data.values())
                    if resolvidos:
                        taxa = (resolvidos['count'] / total) * 100
                        return f"✅ RECLAMAÇÕES RESOLVIDAS:\n• Quantidade: {resolvidos['count']} casos\n• Percentual: {resolvidos['percentage']}%\n• Taxa geral: {taxa:.1f}% do total\n• Status: {'Excelente' if taxa > 80 else 'Crítico' if taxa < 50 else 'Regular'}\n\nQuer estratégias para melhorar?"
                    
                elif any(word in msg_lower for word in ['pendente', 'não resolvido', 'aberta', 'em aberto']):
                    nao_resolvidos = status_data.get('Não resolvido', {})
                    nao_respondidas = status_data.get('Não respondida', {})
                    total_pendentes = (nao_resolvidos.get('count', 0) + nao_respondidas.get('count', 0))
                    return f"⚠️ RECLAMAÇÕES PENDENTES:\n• Não resolvidas: {nao_resolvidos.get('count', 0)} ({nao_resolvidos.get('percentage', 0)}%)\n• Não respondidas: {nao_respondidas.get('count', 0)} ({nao_respondidas.get('percentage', 0)}%)\n• Total pendente: {total_pendentes} casos\n• Prioridade: ALTA - Requer ação imediata!\n\nPrecisa de plano de ação?"
                    
                else:
                    # Resumo geral dos status
                    return f"📋 RESUMO DOS STATUS:\n" + "\n".join([f"• {status}: {data['count']} ({data['percentage']}%)" for status, data in sorted_status]) + f"\n\nTotal analisado: {sum(s['count'] for s in status_data.values())} reclamações"
        
        return "Para ver o status das reclamações, digite 'analisar reclamações' para carregar os dados."
    
    # Perguntas sobre funcionalidades
    if any(word in msg_lower for word in ['funcionalidade', 'função', 'fazer', 'pode', 'ajuda', 'sistema', 'usar']):
        if context_data:
            total = context_data.get('total_reclamacoes', 0)
            return f"🤖 SISTEMA DE ANÁLISE DE RECLAMAÇÕES SICREDI\n\n📊 DADOS DISPONÍVEIS:\n• {total} reclamações analisadas\n• Múltiplas categorias (App, Cartão, PIX, etc.)\n• Status de resolução detalhado\n\n🔍 O QUE POSSO FAZER:\n• Consultar situação atual\n• Identificar categorias críticas\n• Sugerir melhorias\n• Gerar relatórios PDF\n• Enviar análises por email\n\n💬 EXEMPLOS DE PERGUNTAS:\n• 'Qual a situação atual?'\n• 'Categoria mais problemática?'\n• 'Como melhorar o atendimento?'\n• 'Gerar relatório completo'\n\nO que gostaria de saber?"
        return "🤖 Sistema de análise de reclamações do Sicredi. Digite 'analisar reclamações' para carregar os dados e ver todas as funcionalidades disponíveis."
    
    # Perguntas sobre situação atual
    if any(word in msg_lower for word in ['situação', 'status', 'como está', 'resumo', 'geral']):
        if context_data:
            total = context_data.get('total_reclamacoes', 0)
            categorias = len(context_data.get('categorias', {}))
            status_data = context_data.get('status', {})
            resolvidos = status_data.get('Resolvido', {}).get('count', 0) if status_data else 0
            taxa_resolucao = (resolvidos / total * 100) if total > 0 else 0
            
            # Categoria mais crítica
            cats = context_data.get('categorias', {})
            categoria_critica = max(cats.items(), key=lambda x: x[1]['count'])[0] if cats else 'N/A'
            
            status_icon = '🔴' if taxa_resolucao < 50 else '🟡' if taxa_resolucao < 70 else '🟢'
            
            return f"📊 SITUAÇÃO ATUAL DAS RECLAMAÇÕES:\n\n📈 NÚMEROS GERAIS:\n• Total: {total} reclamações\n• Categorias: {categorias} diferentes\n• Mais crítica: {categoria_critica}\n\n{status_icon} RESOLUÇÃO:\n• Taxa atual: {taxa_resolucao:.1f}%\n• Status: {'CRÍTICO - Ação urgente!' if taxa_resolucao < 50 else 'ATENÇÃO - Melhorias necessárias' if taxa_resolucao < 70 else 'BOM - Dentro do esperado'}\n\n💡 PRÓXIMOS PASSOS:\n• 'Como melhorar?' - Recomendações\n• 'Gerar relatório' - Análise completa\n• 'Categoria crítica' - Detalhes do maior problema"
        return "Para ver a situação atual, preciso analisar os dados. Digite 'analisar reclamações'."
    
    # Perguntas sobre melhorias
    if any(word in msg_lower for word in ['melhorar', 'resolver', 'solução', 'como', 'recomendação', 'sugestão']):
        if context_data:
            status_data = context_data.get('status', {})
            cats = context_data.get('categorias', {})
            categoria_critica = max(cats.items(), key=lambda x: x[1]['count'])[0] if cats else 'App'
            nao_resolvidos = sum(dados['count'] for status, dados in status_data.items() if status != 'Resolvido')
            
            return f"💡 RECOMENDAÇÕES ESTRATÉGICAS:\n\n🚨 AÇÕES IMEDIATAS:\n• Resolver {nao_resolvidos} casos pendentes\n• Força-tarefa para categoria {categoria_critica}\n• SLA de 48h para novas reclamações\n\n🔧 MELHORIAS DE PROCESSO:\n• Revisar fluxo de {categoria_critica.lower()}\n• Treinamento específico da equipe\n• Automatizar respostas padrão\n\n📊 MONITORAMENTO:\n• Dashboard em tempo real\n• Alertas automáticos\n• Relatórios semanais\n\n🎯 META: Elevar resolução para >80% em 30 dias\n\nQuer o plano detalhado em PDF?"
        return "💡 Para recomendações específicas, preciso analisar os dados primeiro. Digite 'analisar reclamações'."
    
    # Comandos de análise
    if any(word in msg_lower for word in ['analisar', 'relatório', 'gerar', 'pdf', 'completo']):
        return "📋 ANÁLISE COMPLETA DISPONÍVEL:\n\n🔍 O QUE SERÁ GERADO:\n• Estatísticas detalhadas por categoria\n• Gráficos de distribuição\n• Análise de tendências temporais\n• Insights estratégicos com IA\n• Recomendações de melhoria\n• Relatório PDF profissional\n\n⚡ OPÇÕES:\n• 'Gerar relatório' - PDF local\n• 'Enviar para email@exemplo.com' - PDF por email\n• 'Análise rápida' - Apenas insights\n\nQual opção prefere?"
    


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
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_file_path = os.path.join(os.path.dirname(current_dir), "data", "reclamacoes_20251001_220605.json")
        
        # Verificar se o arquivo existe
        if not os.path.exists(json_file_path):
            return {
                "result": "Erro: Arquivo de reclamações não encontrado.",
                "status": "error"
            }
        
        # Criar instância do analisador
        analyzer = Analyzer(json_file_path)
        
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
        
        # O analyzer já vai salvar na pasta results automaticamente
        pdf_success = analyzer.generate_pdf_report(pdf_filename)
        
        # Ajustar o caminho do arquivo para referência completa
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
        
        # Gerar insights estratégicos
        analysis_context = {
            "taxa_resolucao": taxa_resolucao,
            "total_reclamacoes": total,
            "categorias": categoria_analysis,
            "status": status_analysis,
            "trends": trends_serializable
        }
        
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

def executar_analise_rapida(email_destinatario=None):
    """Execução rápida e limpa do sistema de análise"""
    print("🤖 AGENTE IA - ANÁLISE DE RECLAMAÇÕES SICREDI")
    print("=" * 60)
    
    # Verificar se o arquivo de dados existe
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(os.path.dirname(current_dir), "data", "reclamacoes_20251001_220605.json")
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
        