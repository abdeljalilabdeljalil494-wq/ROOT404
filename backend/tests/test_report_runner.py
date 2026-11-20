"""Redaction regression without external execution."""
from scripts.report_run import redact


def test_report_redacts_env_credentials_authorization_and_url_userinfo(monkeypatch):
    monkeypatch.setenv('EXAMPLE_API_KEY','private-api-value')
    monkeypatch.setenv('GOOGLE_CLIENT_SECRET','private-google-value')
    text=redact('private-api-value private-google-value Authorization: Bearer opaque-token https://name:pass@example.com/path')
    assert all(secret not in text for secret in ['private-api-value','private-google-value','opaque-token','name:pass'])
