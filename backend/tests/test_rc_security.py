"""Separate negative-test assessment. Not an independent external pentest."""
from fastapi.testclient import TestClient
from app.main import app
from app.core.logging import SecretFilter
import logging
client=TestClient(app)


def test_chunked_oversized_body_is_rejected_even_without_content_length():
    def chunks():
        for _ in range(11):yield b'x'*(1024*1024)
    response=client.post('/api/auth/otp',content=chunks(),headers={'Content-Type':'application/json'})
    assert response.status_code==413


def test_invalid_body_length_is_not_silently_ignored():
    assert client.post('/api/auth/otp',content=b'{}',headers={'Content-Length':'invalid'}).status_code==400


def test_log_newline_injection_is_single_line_and_bounded():
    record=logging.LogRecord('test',logging.INFO,'',1,'attacker\r\nFAKE ADMIN LOGIN '+('x'*10000),(),None)
    SecretFilter().filter(record)
    assert '\n' not in record.msg and '\r' not in record.msg and len(record.msg)<=4096
