import httpx
from pydantic import HttpUrl


class URLSubscriber:
    """SNSのsubscribe_urlを検証するクラス"""

    async def subscribe(self, url: HttpUrl) -> bool:
        """
        subscribe_urlにアクセスして購読確認を行うメソッド
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(str(url))
            return response.is_success


def get_url_subscriber() -> URLSubscriber:
    return URLSubscriber()
