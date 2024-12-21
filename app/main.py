import logging
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from app.models import (
    sns_message_adapter,
)
from app.settings import Settings, get_settings
from app.signature import SignatureVerifier, get_signature_verifier
from app.subscriber import URLSubscriber, get_url_subscriber

app = FastAPI()


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@app.post("/")
async def sns_receiver(
    request: Request,
    signature_verifier: Annotated[SignatureVerifier, Depends(get_signature_verifier)],
    url_subscriber: Annotated[URLSubscriber, Depends(get_url_subscriber)],
    settings: Annotated[Settings, Depends(get_settings)],
):
    """
    SNSメッセージを受信して処理するエンドポイント
    """
    try:
        # text/plain で送られてくるため、引数にはせず、json に変換
        message = sns_message_adapter.validate_json(await request.body())
    except ValidationError as e:
        raise RequestValidationError(e.errors())

    if message.topic_arn != settings.sns_topic_arn:
        raise HTTPException(status_code=400, detail="Invalid TopicArn")

    if not await signature_verifier.verify(message):
        raise HTTPException(status_code=400, detail="Invalid signature")

    if message.type == "SubscriptionConfirmation":
        if await url_subscriber.subscribe(message.subscribe_url):
            return {"status": "success", "message": "Subscription confirmed"}
        raise HTTPException(status_code=400, detail="Invalid SubscribeURL")

    elif message.type == "Notification":
        logger.info(f"Received SNS message: {message.message}")
        return {"status": "success", "message": "Message received"}

    elif message.type == "UnsubscribeConfirmation":
        return {"status": "success", "message": "Unsubscribe confirmed"}
