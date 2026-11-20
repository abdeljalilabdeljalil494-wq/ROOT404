"""Loopback-only real STARTTLS SMTP sink for integration tests, NOT Internet mail.

No relay. Delivered messages are private files, never logged. Certificates and
spool live in ignored .cache. External mail reputation/delivery is not tested.
"""
from pathlib import Path
import os
import signal
import ssl
import uuid
from aiosmtpd.controller import Controller

root = Path('.cache/infrastructure').resolve()
spool = root/'mail'
spool.mkdir(mode=0o700, exist_ok=True)


class Sink:
    async def handle_RCPT(self, server, session, envelope, address, options):
        if not address.endswith(('@root404.test', '@example.com')):
            return '550 Local test recipients only'
        envelope.rcpt_tos.append(address)
        return '250 OK'

    async def handle_DATA(self, server, session, envelope):
        fd = os.open(spool/(uuid.uuid4().hex+'.eml'), os.O_WRONLY|os.O_CREAT|os.O_EXCL, 0o600)
        with os.fdopen(fd, 'wb') as output:
            output.write(envelope.original_content)
        return '250 Stored in local verification mailbox'


context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.minimum_version = ssl.TLSVersion.TLSv1_2
context.load_cert_chain(root/'smtp.pem', root/'smtp.key')
controller = Controller(Sink(), hostname='127.0.0.1', port=5587, tls_context=context,
                        require_starttls=True, data_size_limit=65536)
controller.start()
try:
    print('Local STARTTLS SMTP sink ready; no external delivery', flush=True)
    signal.pause()
finally:
    controller.stop()
