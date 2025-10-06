# 🤖 Agente de IA - Análise de Reclamações Sicredi

## 🚀 **NOVO: Agente de IA Conversacional**
```bash
# Chat interativo com IA
python ai_chat_demo.py

# Servidor Bedrock IA
python bedrock_ai_server.py

# Análise rápida (modo clássico)
python my_agent.py
python my_agent.py destinatario@email.com
```

### 🧠 **Capacidades da IA:**
- ✅ **Conversação natural** sobre dados
- ✅ **Insights inteligentes** com Claude 3 Sonnet
- ✅ **Recomendações estratégicas** personalizadas
- ✅ **Análise automática** quando solicitada
- ✅ **Integração Bedrock AgentCore** completa
- ✅ **API REST** para aplicações

## 🛠️ Funcionalidades Principais Ações

**Agente de IA conversacional** desenvolvido com **Amazon Bedrock AgentCore** e **Claude 3 Sonnet** para análise inteligente de reclamações, conversação natural sobre dados e geração de insights estratégicos.

## 🤖 Funcionalidades de IA

- ✅ **Chat conversacional** com dados de reclamações
- ✅ **IA generativa** (Claude 3 Sonnet) para insights
- ✅ **Análise automática** quando solicitada
- ✅ **Relatórios PDF** com insights de IA
- ✅ **Recomendações dinâmicas** personalizadas
- ✅ **API Bedrock** para integração
- ✅ **Servidor IA** para aplicações
- ✅ **Envio automático por e-mail** 📧

## 📊 Principais Métricas Analisadas

### Categorias Identificadas
- **Cartão** (20% das reclamações)
- **App** (20% das reclamações) 
- **PIX** (15% das reclamações)
- **Cobrança** (15% das reclamações)
- **Atendimento** (15% das reclamações)
- **Conta** (15% das reclamações)

### Status das Reclamações
- **Não respondida**: 35% ⚠️
- **Não resolvido**: 30% ⚠️
- **Resolvido**: 20% ✅
- **Respondida**: 15% ⚠️

### 🚨 **Alerta Crítico**: Taxa de resolução de apenas 20%

## �️ Funcionalidades Principais

- **Análise de Dados**: Processa reclamações do arquivo JSON
- **Insights Inteligentes**: Calcula estatísticas e identifica padrões
- **Relatório PDF**: Gera documento profissional com gráficos
- **Resumo Textual**: Cria análise detalhada em formato texto
- **Amazon Bedrock**: Integra com serviços de IA da AWS

## 📊 Análises Realizadas

### Categorias Analisadas
- **Cartão**: 20% das reclamações (4 casos)
- **App**: 20% das reclamações (4 casos)
- **PIX**: 15% das reclamações (3 casos)
- **Cobrança**: 15% das reclamações (3 casos)
- **Atendimento**: 15% das reclamações (3 casos)
- **Conta**: 15% das reclamações (3 casos)

### Status das Reclamações
- **Não respondida**: 35% (7 casos)
- **Não resolvido**: 30% (6 casos)
- **Resolvido**: 20% (4 casos)
- **Respondida**: 15% (3 casos)

### Insights Principais
- 📈 **Taxa de resolução**: 20.0%
- ⚠️ **Problemas pendentes**: 65.0% (13 casos)
- 🎯 **Categoria mais problemática**: Cartão e App (empate com 20%)

## 🛠️ Instalação e Uso

### Pré-requisitos
- Python 3.13+
- **AWS CLI configurado** (credenciais)
- **Amazon Bedrock** com Claude habilitado
- Amazon Bedrock AgentCore SDK
- Dependências listadas em `requirements.txt`

### Instalação
1. Clone o repositório
2. Instale as dependências:
```bash
pip install -r requirements.txt
```
3. Configure as credenciais de e-mail (opcional):
```bash
cp .env.example .env
# Edite o arquivo .env com suas credenciais
```

### 🤖 **Usar Agente de IA (Recomendado)**

```bash
# Chat interativo com IA
python ai_chat_demo.py

# Servidor Bedrock para aplicações
python bedrock_ai_server.py
```

### 📊 **Análise Rápida (Clássico)**

```bash
# Análise básica
python my_agent.py

# Análise com envio de e-mail
python my_agent.py destinatario@email.com
```

## 📁 Estrutura do Projeto

```
├── my_agent.py                    # 🤖 Agente IA principal
├── ai_chat_demo.py                # 💬 Demo chat conversacional
├── bedrock_ai_server.py           # 🚀 Servidor Bedrock IA
├── reclamacoes_analyzer.py        # 📊 Motor de análise
├── email_sender.py                # 📧 Envio de e-mail
├── GUIA_AGENTE_IA.md              # 📖 Guia do agente IA
├── reclamacoes_20251001_220605.json # 📄 Dados de entrada
├── requirements.txt               # 📦 Dependências (+ boto3)
├── .bedrock_agentcore.yaml        # ⚙️ Configuração Bedrock
└── README.md                      # 📚 Este arquivo
```

## 🔧 Arquivos Principais

### `my_agent.py`
Agente principal que integra com Amazon Bedrock AgentCore. Processa payloads e retorna análises estruturadas.

### `reclamacoes_analyzer.py`
Classe principal com métodos para:
- Carregamento de dados JSON
- Análise estatística
- Geração de gráficos
- Criação de relatórios PDF

### `email_sender.py`
Módulo para envio de e-mail com:
- Configuração SMTP
- Anexo de arquivos PDF
- Corpo do e-mail personalizado
- Suporte a credenciais seguras

## 📈 Saídas do Sistema

### Arquivos Gerados
- **PDF**: `relatorio_reclamacoes_YYYYMMDD_HHMMSS.pdf`
- **Gráficos**: Integrados no PDF (categorias, status, timeline)
- **E-mail**: Enviado automaticamente com PDF anexo 📧

### Estrutura do Relatório PDF
1. Resumo executivo
2. Tabelas estatísticas
3. Gráficos de distribuição
4. Análise temporal
5. Insights estratégicos

## 🧠 Exemplos de IA Conversacional

### **Perguntas que a IA responde:**
- *"Qual a situação atual das reclamações?"*
- *"Por que temos tantos problemas com cartão?"*
- *"Como posso melhorar o atendimento?"*
- *"Que ações você recomenda para o PIX?"*
- *"Analisar reclamações e gerar relatório"*

### **Insights Gerados pela IA:**
- 📈 **Análise contextualizada** dos dados
- 🎯 **Recomendações específicas** por categoria
- 📊 **Tendências e padrões** identificados
- 🚀 **Ações estratégicas** personalizadas
- 💡 **Soluções inovadoras** baseadas em IA

## 🐳 Deploy com Docker

```bash
# Build da imagem
docker build -t bedrock-reclamacoes .

# Executar container
docker run -p 8080:8080 bedrock-reclamacoes
```

## 📊 Métricas de Qualidade

- **Taxa de Resolução**: 20.0% ⚠️ (Meta: >80%)
- **Tempo de Resposta**: 65% respondidas ⚠️ (Meta: >90%)
- **Categorização**: 100% das reclamações categorizadas ✅

## 📧 Configuração de E-mail

### Gmail (Recomendado)
1. Ative a verificação em duas etapas
2. Gere uma senha de app: https://myaccount.google.com/apppasswords
3. Configure no arquivo `.env`:
```
EMAIL_SENDER=seu_email@gmail.com
EMAIL_PASSWORD=sua_senha_de_app
```

### Outros Provedores
Ajuste as configurações SMTP no `email_sender.py`

## 🔮 Próximas Melhorias

- [x] **Agente IA conversacional** ✅
- [x] **Integração Bedrock Claude** ✅
- [x] **Chat interativo** ✅
- [x] **Servidor IA** ✅
- [ ] Análise de sentimento avançada
- [ ] Predição com machine learning
- [ ] Dashboard web interativo
- [ ] Alertas inteligentes
- [ ] Integração multi-fontes

## 📝 Logs e Monitoramento

O sistema integra com AWS OpenTelemetry para:
- Rastreamento de execução
- Métricas de performance
- Logs estruturados
- Alertas de erro

## 🤝 Contribuição

1. Fork do projeto
2. Criar branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push (`git push origin feature/nova-funcionalidade`)
5. Pull Request

---

**🤖 Agente de IA desenvolvido com Amazon Bedrock AgentCore + Claude 3 Sonnet** 🚀

📖 **Leia o [GUIA_AGENTE_IA.md](GUIA_AGENTE_IA.md) para usar todas as funcionalidades de IA!**