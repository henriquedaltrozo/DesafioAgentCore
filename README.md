# Agente de IA – Análise de Reclamações Sicredi

Um agente inteligente para análise automatizada de reclamações do Sicredi, desenvolvido com **Bedrock AgentCore** e utilizando **Amazon Bedrock** para IA generativa, processamento de linguagem natural e envio de relatórios por email.

## Visão Geral
Este projeto automatiza a análise de reclamações recebidas, gera relatórios em PDF e pode enviá-los por email. Utiliza:
- **Bedrock AgentCore**: Framework para estruturar o agente de IA
- **Amazon Bedrock**: Serviço de IA generativa (Claude Nova Micro) para análise e conversação
- **Processamento inteligente**: Sumarização e classificação automática dos dados

## Funcionalidades
- Análise automática de reclamações (JSON)
- Geração de relatórios em PDF
- Chat interativo com IA para dúvidas e análises
- Envio automático de relatórios por email (Gmail)

## Pré-requisitos
- Python 3.13+
- AWS CLI configurado (com credenciais válidas)
- **Amazon Bedrock** habilitado na região us-east-1
- Acesso ao modelo **Claude Nova Micro** no Bedrock
- **Bedrock AgentCore SDK** (`bedrock-agentcore`)
- Dependências listadas em `requirements.txt`
- Conta Gmail com autenticação em duas etapas (opcional, para envio de email)

## Instalação
1. Clone este repositório:
	```bash
	git clone <url-do-repositorio>
	cd DesafioAgentCore
	```
2. Instale as dependências:
	```bash
	pip install -r requirements.txt
	```

## Configuração do Ambiente
1. **AWS CLI:**
	- Configure suas credenciais AWS:
	  ```bash
	  aws configure
	  ```
2. **Gmail (opcional, para envio de email):**
	- Ative a verificação em duas etapas na sua conta Google
	- Gere uma senha de app: https://myaccount.google.com/apppasswords
	- Crie um arquivo `.env` na raiz do projeto com:
	  ```env
	  GMAIL_USER=seu_email@gmail.com
	  GMAIL_PASS=sua_senha_de_app
	  ```

## Como Usar

### Chat interativo com IA
```bash
python src/ai_chat_demo.py
```

### Gerar análise de reclamações
```bash
python src/my_agent.py
```

### Gerar análise e enviar por email
```bash
python src/my_agent.py destinatario@email.com
```

Os relatórios gerados ficam na pasta `results/`.
