import base64
import logging
from typing import cast

import httpx
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from app.models import SNSMessage

logger = logging.getLogger(__name__)


class SignatureVerifier:
    """SNSメッセージの署名を検証するクラス"""

    async def verify(self, message: SNSMessage) -> bool:
        """
        SNSメッセージの署名検証を行うメソッド
        """
        signable = ""
        if message.type == "Notification":
            signable += f"Message\n{message.message}\n"
            signable += f"MessageId\n{message.message_id}\n"
            if message.subject:
                signable += f"Subject\n{message.subject}\n"
            signable += f"Timestamp\n{message.timestamp}\n"
            signable += f"TopicArn\n{message.topic_arn}\n"
            signable += f"Type\n{message.type}\n"
        else:
            signable += f"Message\n{message.message}\n"
            signable += f"MessageId\n{message.message_id}\n"
            signable += f"SubscribeURL\n{message.subscribe_url}\n"
            signable += f"Timestamp\n{message.timestamp}\n"
            signable += f"Token\n{message.token}\n"
            signable += f"TopicArn\n{message.topic_arn}\n"
            signable += f"Type\n{message.type}\n"

        cert_url = str(message.signing_cert_url)
        if not cert_url or "amazonaws.com" not in cert_url:
            logger.warning(f"Invalid SigningCertURL: {cert_url}")
            return False

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(cert_url, timeout=5)
                response.raise_for_status()
                cert_pem = response.text
        except Exception as e:
            logger.error(f"Failed to fetch certificate: {str(e)}")
            return False

        decoded_signature = base64.b64decode(message.signature)

        cert = x509.load_pem_x509_certificate(cert_pem.encode("utf-8"))
        public_key = cast(rsa.RSAPublicKey, cert.public_key())
        sig_ver = message.signature_version
        logger.debug(f"Verifying signature with version {sig_ver}")
        try:
            public_key.verify(
                decoded_signature,
                signable.encode("utf-8"),
                padding.PKCS1v15(),
                hashes.SHA256() if sig_ver == "2" else hashes.SHA1(),
            )
            return True
        except Exception as e:
            logger.error(f"Signature verification failed: {str(e)}")
            return False


def get_signature_verifier() -> SignatureVerifier:
    return SignatureVerifier()
