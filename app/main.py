import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from app.models import (
    sns_message_adapter,
)

app = FastAPI()


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@app.post("/")
async def sns_receiver(
    request: Request,
):
    try:
        # text/plain で送られてくるため、引数にはせず、json に変換
        message = sns_message_adapter.validate_json(await request.body())
    except ValidationError as e:
        raise RequestValidationError(e.errors())

    return "ok"
