import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional
from services.email_service_interface import EmailServiceInterface
from configs.config import getenv


class LegacyGmailService(EmailServiceInterface):
    def __init__(self, email: str = "", app_password: str = ""):
        """
        Inicializa o serviço de email usando SMTP e senha de aplicativo

        Args:
            email: Email do remetente
            app_password: Senha de aplicativo gerada pelo Google
        """
        self.email = getenv("EMAIL", email)
        self.app_password = getenv("SENHA_EMAIL", app_password)
        self.smtp_port = getenv("EMAIL_PORT", 587)
        self.smtp_server = getenv("EMAIL_HOST", 'smtp.gmail.com')

    def send_email(
        self,
        sender_email: str,
        recipients: List[str],
        subject: str,
        body: str,
        body_html: bool = False,
        attachments: Optional[List[str]] = None
    ):
        """
        Envia email usando o servidor SMTP do Gmail
        """
        try:
            # Cria a mensagem
            message = MIMEMultipart()
            message["From"] = sender_email
            message["To"] = ", ".join(recipients)
            message["Subject"] = subject

            # Adiciona o corpo do email
            if body_html:
                message.attach(MIMEText(body, "html"))
            else:
                message.attach(MIMEText(body, "plain"))

            # Adiciona anexos
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as file:
                            part = MIMEBase("application", "octet-stream")
                            part.set_payload(file.read())

                        encoders.encode_base64(part)
                        part.add_header(
                            "Content-Disposition",
                            f"attachment; filename={os.path.basename(file_path)}"
                        )
                        message.attach(part)

            # Conecta ao servidor SMTP do Gmail
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Iniciar conexão segura
                server.login(self.email, self.app_password)
                server.sendmail(sender_email, recipients, message.as_string())

            print(
                f"✅ Email enviado com sucesso para {len(recipients)} destinatário(s)")
            return True

        except Exception as e:
            print(f"❌ Erro ao enviar email: {e}")
            return False
