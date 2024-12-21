import logging

from fastapi import FastAPI, Request

app = FastAPI()


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@app.post("/")
async def sns_receiver(request: Request):
    return "ok"
