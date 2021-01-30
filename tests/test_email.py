import pytest

from app.internal.email import mail
from fastapi import BackgroundTasks, status


def test_email_send(client, user, event, smtpd):
    mail.config.SUPPRESS_SEND = 1
    mail.config.MAIL_SERVER = smtpd.hostname
    mail.config.MAIL_PORT = smtpd.port
    mail.config.USE_CREDENTIALS = False
    mail.config.MAIL_TLS = False
    with mail.record_messages() as outbox:
        response = client.post(
            "/email/send", data={
                "event_used": event.id, "user_to_send": user.id,
                "title": "Testing",
                "background_tasks": BackgroundTasks})
        assert len(outbox) == 1
        assert response.ok


def test_failed_email_send(client, user, event, smtpd):
    mail.config.SUPPRESS_SEND = 1
    mail.config.MAIL_SERVER = smtpd.hostname
    mail.config.MAIL_PORT = smtpd.port
    with mail.record_messages() as outbox:
        response = client.post(
            "/email/send", data={
                "event_used": event.id + 1, "user_to_send": user.id,
                "title": "Testing",
                "background_tasks": BackgroundTasks})
        assert len(outbox) == 0
        assert not response.ok


@pytest.fixture
def configured_smtpd(smtpd):
    """
    Overrides the SMTP related configuration to use a mock SMTP server
    :param smtpd: the smtpdfix fixture that represents an SMTP server
    :return: smtpd
    """

    mail.config.SUPPRESS_SEND = 1
    mail.config.MAIL_SERVER = smtpd.hostname
    mail.config.MAIL_PORT = smtpd.port
    mail.config.USE_CREDENTIALS = False
    mail.config.MAIL_TLS = False
    yield smtpd


def test_send_mail_no_body(client, configured_smtpd):
    with mail.record_messages() as outbox:
        response = client.post("/email/invitation/")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        assert response.json() == {'detail': [{
            'loc': ['body'],
            'msg': 'field required',
            'type': 'value_error.missing'}]}
        assert not outbox


def test_send_mail_invalid_email(client, configured_smtpd):
    with mail.record_messages() as outbox:
        response = client.post("/email/invitation/", json={
            "sender_name": "string",
            "recipient_name": "string",
            "recipient_mail": "test#mail.com"
        })

        assert response.status_code ==\
               status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.json() ==\
               {"detail": "Please enter valid email address"}
        assert not outbox


def assert_validation_error_missing_body_fields(validation_msg,
                                                missing_fields):
    """
    helper function for asserting with open api validation errors
    look at https://fastapi.tiangolo.com/tutorial/path-params/#data-validation
    :param validation_msg: the response message after json
    :param missing_fields: a list of fields that are asserted missing
    """
    assert isinstance(validation_msg, dict)
    assert 1 == len(validation_msg)
    assert "detail" in validation_msg
    details = validation_msg["detail"]
    assert isinstance(details, list)
    assert len(missing_fields) == len(details)
    for detail in details:
        assert 3 == len(detail)
        assert "type" in detail
        assert "value_error.missing" == detail["type"]
        assert "msg" in detail
        assert "field required" == detail["msg"]
        assert "loc" in detail
        loc = detail["loc"]
        assert isinstance(loc, list)
        assert 2 == len(loc)
        assert "body" == loc[0]
        assert loc[1] in missing_fields


@pytest.mark.parametrize("body, missing_fields", [
    (
            {"sender_name": "string", "recipient_name": "string"},
            ["recipient_mail"],
    ),

    (
            {"sender_name": "string", "recipient_mail": "test@mail.com"},
            ["recipient_name"],
    ),
    (
            {"recipient_name": "string", "recipient_mail": "test@mail.com"},
            ["sender_name"],
    ),
    (
            {"sender_name": "string"},
            ["recipient_name", "recipient_mail"],
    ),
    (
            {"recipient_name": "string"},
            ["sender_name", "recipient_mail"],
    ),
    (
            {"recipient_mail": "test@mail.com"},
            ["sender_name", "recipient_name"],
    ),
])
def test_send_mail_partial_body(body, missing_fields,
                                client, configured_smtpd):
    with mail.record_messages() as outbox:
        response = client.post("/email/invitation/", json=body)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert_validation_error_missing_body_fields(response.json(),
                                                    missing_fields)
        assert not outbox


def test_send_mail_valid_email(client, configured_smtpd):
    with mail.record_messages() as outbox:
        response = client.post("/email/invitation/", json={
            "sender_name": "string",
            "recipient_name": "string",
            "recipient_mail": "test@mail.com"
        }
                               )
        assert response.ok
        assert outbox
