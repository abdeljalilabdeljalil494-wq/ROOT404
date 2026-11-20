import pytest
from app.core.config import Settings


@pytest.fixture(autouse=True)
def independent_configuration_environment(monkeypatch):
    # Workflow fixtures explicitly opt in; constructor tests exercise safe defaults.
    monkeypatch.delenv("ENABLE_DEV_OTP", raising=False)


def test_cors_accepts_comma_delimited_and_json():
    assert Settings(CORS_ORIGINS='https://a.example, https://b.example').CORS_ORIGINS == ['https://a.example', 'https://b.example']
    assert Settings(CORS_ORIGINS='["https://a.example"]').CORS_ORIGINS == ['https://a.example']


def test_production_rejects_demo_and_unconfigured_email():
    with pytest.raises(ValueError):
        Settings(ENVIRONMENT='production', SECRET_KEY='x' * 64, EMAIL_PROVIDER='development')
    with pytest.raises(ValueError):
        Settings(ENVIRONMENT='production', SECRET_KEY='x' * 64, EMAIL_PROVIDER='smtp', SMTP_HOST='mail.example.com',
                 SMTP_FROM='root404@example.com', DATABASE_URL='postgresql://localhost/root404', ENABLE_DEMO_FEATURES=True)


def test_enabled_production_judge_requires_tls_and_long_secret():
    base = dict(ENVIRONMENT='production', SECRET_KEY='x'*64, EMAIL_PROVIDER='smtp', SMTP_HOST='mail.example.com',
                SMTP_FROM='root404@example.com', DATABASE_URL='postgresql://localhost/root404', JUDGE_ENABLED=True)
    with pytest.raises(ValueError):
        Settings(**base,JUDGE_URL='http://executor.example.com',JUDGE_SHARED_SECRET='s'*64)
    with pytest.raises(ValueError):
        Settings(**base,JUDGE_URL='https://executor.example.com',JUDGE_SHARED_SECRET='short')
    with pytest.raises(ValueError):
        Settings(**base,JUDGE_URL='https://executor.example.com',JUDGE_SHARED_SECRET='s'*64)
    assert Settings(**base,JUDGE_URL='https://executor.example.com',JUDGE_SHARED_SECRET='s'*64,JUDGE_EXPECTED_IMAGE='root404/jobs@sha256:'+'a'*64).JUDGE_ENABLED


def test_production_oauth_partial_and_unsafe_config_rejected():
    base=dict(ENVIRONMENT='production',SECRET_KEY='x'*64,EMAIL_PROVIDER='smtp',SMTP_HOST='mail.example.com',
              SMTP_FROM='root404@example.com',DATABASE_URL='postgresql://localhost/root404')
    for provider in ['GOOGLE','GITHUB']:
        with pytest.raises(ValueError): Settings(**base,**{provider+'_CLIENT_ID':'id'})
        with pytest.raises(ValueError):
            Settings(**base,**{provider+'_CLIENT_ID':'id',provider+'_CLIENT_SECRET':'private',provider+'_REDIRECT_URI':'http://evil.example/oauth/callback/'+provider.lower()})
        assert Settings(**base,**{provider+'_CLIENT_ID':'id',provider+'_CLIENT_SECRET':'private',provider+'_REDIRECT_URI':'https://beta.example/oauth/callback/'+provider.lower()})
