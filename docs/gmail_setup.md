# Configuração Gmail para Envio de E-mail

## Passo a Passo:

### 1. Ativar Verificação em Duas Etapas
- Acesse: https://myaccount.google.com/security
- Clique em "Verificação em duas etapas"
- Siga as instruções para ativar

### 2. Gerar Senha de App
- Acesse: https://myaccount.google.com/apppasswords
- Selecione "E-mail" como aplicativo
- Selecione "Outro (nome personalizado)"
- Digite: "Sistema Reclamações"
- Clique em "Gerar"
- **COPIE A SENHA GERADA** (16 caracteres)

### 3. Configurar no .env
```
EMAIL_SENDER=seu_email@gmail.com
EMAIL_PASSWORD=sua_senha_de_app_de_16_caracteres
```

### 4. Testar
```bash
python src/my_agent.py destinatario@email.com
```

## Alternativa: Usar Outro Provedor
Se não quiser configurar senha de app, use:
- Outlook.com (senha normal)
- Yahoo (senha normal)
- Outros provedores SMTP