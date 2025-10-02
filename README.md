# 🏦 Sistema de Análise de Reclamações

### **Execução Principal** (Arquivo único)
```bash
python my_agent.py
```

Este é o **único comando necessário** para:
- ✅ Carregar e analisar os dados JSON
- ✅ Gerar insights com IA integrada
- ✅ Criar relatório PDF completo
- ✅ Mostrar resumo na tela
- ✅ Salvar resumo executivo

## 🛠️ Funcionalidades Principais Ações

Sistema desenvolvido com **Amazon Bedrock AgentCore** para análise inteligente de reclamações do Reclame Aqui, geração de insights e relatórios em PDF.

## 🚀 Funcionalidades

- ✅ **Análise automática** de dados JSON de reclamações
- ✅ **Insights inteligentes** com IA (Amazon Bedrock + Strands Agents)  
- ✅ **Relatórios em PDF** com gráficos e visualizações
- ✅ **Resumos executivos** em texto
- ✅ **Recomendações estratégicas** personalizadas
- ✅ **Integração completa** com Bedrock AgentCore

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
- Amazon Bedrock AgentCore SDK
- Dependências listadas em `requirements.txt`

### Instalação
1. Clone o repositório
2. Instale as dependências:
```bash
pip install -r requirements.txt
```

### Executar Análise

# Usar como agente Bedrock
python my_agent.py
```

## 📁 Estrutura do Projeto

```
├── my_agent.py                    # Agente principal do Bedrock
├── reclamacoes_analyzer.py        # Motor de análise de dados
├── reclamacoes_20251001_220605.json # Dados de entrada
├── requirements.txt               # Dependências Python
├── Dockerfile                     # Container Docker
└── .bedrock_agentcore.yaml        # Configuração Bedrock
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

## 📈 Saídas do Sistema

### Arquivos Gerados
- **PDF**: `relatorio_sicredi_YYYYMMDD_HHMMSS.pdf`
- **TXT**: `resumo_sicredi_YYYYMMDD_HHMMSS.txt`
- **Gráficos**: Integrados no PDF (categorias, status, timeline)

### Estrutura do Relatório PDF
1. Resumo executivo
2. Tabelas estatísticas
3. Gráficos de distribuição
4. Análise temporal
5. Insights estratégicos

## 🎯 Insights de Negócio

### Problemas Identificados
- **Alta taxa de não resolução**: 65% das reclamações estão pendentes
- **Problemas recorrentes**: Cartão e App são as categorias mais citadas
- **Tempo de resposta**: 35% das reclamações ainda não foram respondidas

### Recomendações
1. **Priorizar resolução**: Focar nos 65% de casos pendentes
2. **Melhorar App**: Investir em UX e performance da aplicação
3. **Treinamento**: Capacitar equipe para problemas de cartão
4. **Automação PIX**: Implementar soluções para transações PIX

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

## 🔮 Próximas Melhorias

- [ ] Análise de sentimento com NLP
- [ ] Predição de escalação de problemas
- [ ] Dashboard interativo
- [ ] Alertas automáticos
- [ ] Integração com CRM

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

**Desenvolvido com Amazon Bedrock AgentCore** 🚀