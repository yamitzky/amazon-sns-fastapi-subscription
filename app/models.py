from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, TypeAdapter
from pydantic.alias_generators import to_pascal


class SNSMessageBase(BaseModel):
    message_id: str
    topic_arn: str
    timestamp: str
    signature_version: str
    signature: str
    signing_cert_url: Annotated[HttpUrl, Field(alias="SigningCertURL")]
    message: str

    model_config = ConfigDict(
        alias_generator=to_pascal,
        extra="allow",
    )


class SNSNotification(SNSMessageBase):
    type: Literal["Notification"]
    subject: str | None = None


class SNSSubscription(SNSMessageBase):
    type: Literal["SubscriptionConfirmation"]
    subscribe_url: Annotated[HttpUrl, Field(alias="SubscribeURL")]
    token: str


class SNSUnsubscribe(SNSMessageBase):
    type: Literal["UnsubscribeConfirmation"]
    subscribe_url: Annotated[HttpUrl, Field(alias="SubscribeURL")]
    token: str


SNSMessage = Annotated[
    SNSNotification | SNSSubscription | SNSUnsubscribe, Field(discriminator="type")
]
sns_message_adapter: TypeAdapter[SNSMessage] = TypeAdapter(SNSMessage)
