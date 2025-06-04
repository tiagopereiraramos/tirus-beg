from enum import Enum
from typing import List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64
from email.mime.base import MIMEBase
from email import encoders
import os
from util.dataclass import (
    NotificationDetail,
    NotificationType,
)  # Assumindo que NotificationType está no arquivo 'dataclass.py'


class NotificationService:
    def __init__(self, gmail_service):
        self.gmail_service = gmail_service

    def send_notification(
        self,
        recipients: List[str],
        notification_type: NotificationType,
        notification_detail: NotificationDetail,
        message: Optional[str] = None,
        details: Optional[str] = None,
        link: Optional[str] = None,
        attachments: Optional[List[str]] = None,
    ):
        subject = f"Notificação de Automação: {notification_type.value}"
        body_html = self._generate_email_body(
            notification_type, notification_detail, link, attachments
        )

        self.gmail_service.send_email(
            "administrativo@bgtele.com.br",
            recipients,
            subject,
            body_html,
            body_html=True,
            attachments=attachments,
        )

    def _generate_email_body(
        self,
        notification_type: NotificationType,
        notification_detail: NotificationDetail,
        link: Optional[str],
        attachments: Optional[List[str]],
    ) -> str:
        has_attachments = bool(attachments)

        # Gerar HTML detalhado com base no tipo de notificação
        notification_details_html = notification_type.to_html(
            notification_details=notification_detail
        )

        # Estrutura do corpo do e-mail
        email_template = """
        <!DOCTYPE html>
        <html>
        <body>
            {detalhes}
            {link_button}
            {anexo_info}
        </body>
        </html>
        """

        # Complemento para o link e anexos
        link_button_html = (
            f'<p><a href="{link}" style="background:#204f8f;color:#fff;padding:10px;border-radius:5px;text-decoration:none;">Acessar</a></p>'
            if link
            else ""
        )
        anexo_info_html = "<p>Este e-mail contém anexos.</p>" if has_attachments else ""

        # Gerar o corpo do e-mail completo com o HTML detalhado
        return email_template.format(
            titulo=f"Notificação: {notification_type.value}",
            status=notification_type.value,
            detalhes=notification_details_html,  # Aqui insere o HTML dos detalhes gerados pelo to_html()
            link_button=link_button_html,
            anexo_info=anexo_info_html,
        )
