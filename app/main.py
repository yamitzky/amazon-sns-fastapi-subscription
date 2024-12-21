import logging
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from app.models import (
    sns_message_adapter,
)
from app.settings import Settings, get_settings

app = FastAPI()


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@app.post("/")
async def sns_receiver(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
):
    try:
        # text/plain で送られてくるため、引数にはせず、json に変換
        message = sns_message_adapter.validate_json(await request.body())
    except ValidationError as e:
        raise RequestValidationError(e.errors())

    if message.topic_arn != settings.sns_topic_arn:
        raise HTTPException(status_code=400, detail="Invalid TopicArn")

    return "ok"
