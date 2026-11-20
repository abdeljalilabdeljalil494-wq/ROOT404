"""Defense-in-depth log redaction. Do not log request bodies/source in the first place."""
import logging
import re
from .config import settings


class SecretFilter(logging.Filter):
    def filter(self, record):
        message = record.getMessage()
        if record.levelno >= logging.ERROR:
            message = "Operation failed in " + record.name + "; details withheld to protect user data"
        for value in (settings.SECRET_KEY, settings.SMTP_PASSWORD, settings.OPENAI_API_KEY,
                      settings.JUDGE_SHARED_SECRET, settings.GOOGLE_CLIENT_SECRET,
                      settings.GITHUB_CLIENT_SECRET, settings.DATABASE_URL, settings.REDIS_URL):
            if value and len(value) >= 8:
                message = message.replace(value, '[REDACTED]')
        message = re.sub(r'(?i)Bearer\s+[A-Za-z0-9._~+/-]+=*', 'Bearer [REDACTED]', message)
        message = re.sub(r'([a-zA-Z][a-zA-Z0-9+.-]*://)[^\s/@]+:[^\s/@]+@', r'\1[REDACTED]@', message)
        message = re.sub(r'[A-Za-z0-9.!#$%&\x27*+/=?^_`{|}~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', '[EMAIL]', message)
        message = message.replace("\r", " ").replace("\n", " ")[:4096]
        record.msg, record.args = message, ()
        # Traceback messages can embed SQL or client-library errors containing
        # request/credential text. Keep exception type, not arbitrary exception text.
        if record.exc_info:
            record.msg += ' [' + record.exc_info[0].__name__ + ']'
            record.exc_info, record.exc_text = None, None
        return True


def install_secret_filters():
    root = logging.getLogger()
    for handler in root.handlers:
        handler.addFilter(SecretFilter())
    for name in ('uvicorn', 'uvicorn.error', 'uvicorn.access', 'httpx', 'httpcore'):
        for handler in logging.getLogger(name).handlers:
            handler.addFilter(SecretFilter())
