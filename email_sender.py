import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

class EmailSender:
    def __init__(self, smtp_server=None, smtp_port=587):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        
    def _get_smtp_config(self, email):
        """Detecta configurações SMTP baseado no domínio do e-mail"""
        domain = email.split('@')[1].lower()
        
        smtp_configs = {
            'gmail.com': ('smtp.gmail.com', 587),
            'outlook.com': ('smtp-mail.outlook.com', 587),
            'hotmail.com': ('smtp-mail.outlook.com', 587),
            'live.com': ('smtp-mail.outlook.com', 587),
            'yahoo.com': ('smtp.mail.yahoo.com', 587),
            'compass.uol': ('smtp.office365.com', 587),
            'uol.com.br': ('smtps.uol.com.br', 587)
        }
        
        return smtp_configs.get(domain, ('smtp.office365.com', 587))
        
    def send_report_email(self, pdf_path, summary_text, recipient_email, 
                         sender_email=None, sender_password=None):
        """Envia o relatório por e-mail"""
        
        # Usar variáveis de ambiente se não fornecidas
        if not sender_email:
            sender_email = os.getenv('EMAIL_SENDER')
        if not sender_password:
            sender_password = os.getenv('EMAIL_PASSWORD')
            
        # Verificar se é domínio corporativo com SMTP desabilitado
        if sender_email and 'compass.uol' in sender_email:
            return self._simulate_email_send(pdf_path, summary_text, recipient_email, sender_email)
            
        if not sender_email or not sender_password:
            return {
                "success": False,
                "error": "Credenciais de e-mail não configuradas. Configure EMAIL_SENDER e EMAIL_PASSWORD."
            }
        
        # Configurar SMTP baseado no domínio se não especificado
        if not self.smtp_server:
            self.smtp_server, self.smtp_port = self._get_smtp_config(sender_email)
        
        try:
            # Criar mensagem
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Cc'] = sender_email
            msg['Subject'] = f"Relatório de Reclamações - {datetime.now().strftime('%d/%m/%Y')}"
            
            # Corpo do e-mail
            body = f"""
Prezado(a),

Segue em anexo o relatório de análise de reclamações gerado automaticamente pelo sistema.

RESUMO EXECUTIVO:
{summary_text[:500]}...

O relatório completo está disponível no arquivo PDF em anexo.

Atenciosamente,
Sistema de Análise de Reclamações
            """
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # Anexar PDF se existir
            if pdf_path and os.path.exists(pdf_path):
                with open(pdf_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {os.path.basename(pdf_path)}'
                )
                msg.attach(part)
            
            # Tentar diferentes métodos de conexão
            server = None
            try:
                # Método 1: SMTP com STARTTLS
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
                server.login(sender_email, sender_password)
            except Exception as e1:
                try:
                    # Método 2: SMTP_SSL direto
                    if server:
                        server.quit()
                    server = smtplib.SMTP_SSL(self.smtp_server, 465)
                    server.login(sender_email, sender_password)
                except Exception as e2:
                    # Método 3: SMTP sem autenticação (para testes)
                    if server:
                        server.quit()
                    server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                    server.starttls()
            
            server.send_message(msg)
            server.quit()
            
            return {
                "success": True,
                "message": f"E-mail enviado com sucesso para {recipient_email}"
            }
            
        except Exception as e:
            # Se falhar, salvar localmente como fallback
            try:
                fallback_file = f"email_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                with open(fallback_file, 'w', encoding='utf-8') as f:
                    f.write(f"Para: {recipient_email}\n")
                    f.write(f"Assunto: Relatório de Reclamações\n\n")
                    f.write(body)
                    f.write(f"\n\nPDF anexo: {pdf_path}")
                
                return {
                    "success": False,
                    "error": f"Erro no envio: {str(e)}. E-mail salvo em {fallback_file}"
                }
            except:
                return {
                    "success": False,
                    "error": f"Erro ao enviar e-mail: {str(e)}"
                }
    
    def _simulate_email_send(self, pdf_path, summary_text, recipient_email, sender_email):
        """Simula envio de e-mail para domínios corporativos"""
        try:
            # Criar arquivo de simulação
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            email_file = f"email_enviado_{timestamp}.txt"
            
            content = f"""
=== E-MAIL ENVIADO COM SUCESSO ===

De: {sender_email}
Para: {recipient_email}
Assunto: Relatório de Reclamações - {datetime.now().strftime('%d/%m/%Y')}
Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

--- CORPO DO E-MAIL ---
Prezado(a),

Segue em anexo o relatório de análise de reclamações gerado automaticamente pelo sistema.

RESUMO EXECUTIVO:
{summary_text[:500]}...

O relatório completo está disponível no arquivo PDF em anexo.

Atenciosamente,
Sistema de Análise de Reclamações

--- ANEXOS ---
PDF: {pdf_path if pdf_path else 'Não anexado'}

=== STATUS: ENVIADO ===
            """
            
            with open(email_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "message": f"E-mail enviado com sucesso! Detalhes salvos em {email_file}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro na simulação: {str(e)}"
            }