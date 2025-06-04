from typing import List, Optional


class BaseEmailService:
    def send_email(
        self,
        sender: str,
        recipients: List[str],
        subject: str,
        body: str,
        body_html: bool = False,
        attachments: Optional[List[str]] = None,
    ):
        raise NotImplementedError("Este método deve ser implementado.")
