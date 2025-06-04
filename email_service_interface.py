from abc import ABC, abstractmethod
from typing import List, Optional


class EmailServiceInterface(ABC):
    @abstractmethod
    def send_email(
        self,
        sender_email: str,
        recipients: List[str],
        subject: str,
        body: str,
        body_html: bool = False,
        attachments: Optional[List[str]] = None
    ):
        """Envia um email com os parâmetros fornecidos"""
        pass
