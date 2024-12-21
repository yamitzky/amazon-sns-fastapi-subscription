import pytest
from fastapi.testclient import TestClient

from app import app
from app.settings import Settings, get_settings
from app.signature import get_signature_verifier
from app.subscriber import get_url_subscriber

client = TestClient(app)


@pytest.fixture
def valid_notification():
    return {
        "Type": "Notification",
        "MessageId": "test-message-id",
        "TopicArn": "arn:aws:sns:region:123456789012:test-topic",
        "Message": "Test message",
        "Timestamp": "2023-01-01T00:00:00.000Z",
        "SignatureVersion": "1",
        "Signature": "test-signature",
        "SigningCertURL": "https://sns.us-east-1.amazonaws.com/cert.pem",
        "Subject": "Test Subject",
    }


@pytest.fixture
def valid_subscription():
    return {
        "Type": "SubscriptionConfirmation",
        "MessageId": "test-message-id",
        "TopicArn": "arn:aws:sns:region:123456789012:test-topic",
        "Message": "Test message",
        "Timestamp": "2023-01-01T00:00:00.000Z",
        "SignatureVersion": "1",
        "Signature": "test-signature",
        "SigningCertURL": "https://sns.us-east-1.amazonaws.com/cert.pem",
        "SubscribeURL": "https://sns.us-east-1.amazonaws.com/subscribe",
        "Token": "test-token",
    }


@pytest.fixture
def mock_get_verifier(mocker):
    """署名検証のモックを提供するフィクスチャ"""
    mock_verifier = mocker.Mock()
    mock_verifier.verify = mocker.AsyncMock(return_value=True)
    return lambda: mock_verifier


@pytest.fixture
def mock_get_subscriber(mocker):
    """subscribe_url検証のモックを提供するフィクスチャ"""
    mock_subscriber = mocker.Mock()
    mock_subscriber.subscribe = mocker.AsyncMock(return_value=True)
    return lambda: mock_subscriber


@pytest.fixture
def mock_get_settings():
    return lambda: Settings(sns_topic_arn="arn:aws:sns:region:123456789012:test-topic")


@pytest.fixture(autouse=True)
def reset_dependency_overrides(
    mock_get_verifier, mock_get_subscriber, mock_get_settings
):
    app.dependency_overrides = {}
    app.dependency_overrides[get_signature_verifier] = mock_get_verifier
    app.dependency_overrides[get_url_subscriber] = mock_get_subscriber
    app.dependency_overrides[get_settings] = mock_get_settings
    yield
    app.dependency_overrides = {}


def test_notification_endpoint_with_invalid_json():
    """不正なJSONを送信した場合のテスト"""
    response = client.post("/", content="invalid json")
    assert response.status_code == 422


def test_notification_endpoint_with_invalid_signature(valid_notification, mocker):
    """不正な署名を送信した場合のテスト"""
    mock_verifier = mocker.Mock()
    mock_verifier.verify = mocker.AsyncMock(return_value=False)
    app.dependency_overrides[get_signature_verifier] = lambda: mock_verifier

    invalid_signature = valid_notification
    response = client.post("/", json=invalid_signature)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid signature"


def test_notification_endpoint_with_invalid_type(valid_notification):
    """不正なTypeを送信した場合のテスト"""
    invalid_type = valid_notification
    invalid_type["Type"] = "InvalidType"
    response = client.post("/", json=invalid_type)
    assert response.status_code == 422


def test_notification_endpoint_with_missing_required_field(valid_notification):
    """必須フィールドが欠けている場合のテスト"""
    invalid_data = valid_notification
    del invalid_data["MessageId"]
    response = client.post("/", json=invalid_data)
    assert response.status_code == 422


def test_notification_endpoint_with_invalid_url(valid_notification):
    """不正なURLを送信した場合のテスト"""
    invalid_url = valid_notification
    invalid_url["SigningCertURL"] = "not-a-url"
    response = client.post("/", json=invalid_url)
    assert response.status_code == 422


def test_notification_endpoint_with_invalid_topic(valid_notification):
    """不正なTopicArnを送信した場合のテスト"""
    invalid_topic = valid_notification
    invalid_topic["TopicArn"] = "arn:aws:sns:region:123456789012:wrong-topic"
    response = client.post("/", json=invalid_topic)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid TopicArn"


def test_notification_endpoint_success(valid_notification):
    """正常なSNS通知を送信した場合のテスト"""
    response = client.post("/", json=valid_notification)
    assert response.status_code == 200
    assert response.json() == {"status": "success", "message": "Message received"}


def test_subscription_confirmation_success(valid_subscription):
    """正常なサブスクリプション確認を送信した場合のテスト"""
    response = client.post("/", json=valid_subscription)
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "Subscription confirmed",
    }


def test_unsubscribe_confirmation_success(valid_subscription):
    """正常な購読解除確認を送信した場合のテスト"""
    unsubscribe_data = valid_subscription
    unsubscribe_data["Type"] = "UnsubscribeConfirmation"
    response = client.post("/", json=unsubscribe_data)
    assert response.status_code == 200
    assert response.json() == {"status": "success", "message": "Unsubscribe confirmed"}
