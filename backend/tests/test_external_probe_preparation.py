"""Probe preparation tests with doubles only; NOT live external-service evidence."""
from types import SimpleNamespace
import pytest
from scripts import verify_external_integrations as probes


def test_missing_optin_never_calls_service_or_exposes_private_exception(monkeypatch):
    probes.results.clear()
    monkeypatch.setenv('PROBE_TEST_SECRET','private-sentinel')
    monkeypatch.delenv('ROOT404_ALLOW_EXTERNAL_PROBES',raising=False)
    probes.probe('test',['PROBE_TEST_SECRET'],lambda:pytest.fail('Unauthorized external call'))
    assert probes.results['test']['status']=='BLOCKED'
    monkeypatch.setenv('ROOT404_ALLOW_EXTERNAL_PROBES','yes')
    def failure(): raise RuntimeError('private-sentinel credentials in unsafe error text')
    probes.probe('test',['PROBE_TEST_SECRET'],failure)
    assert probes.results['test']['status']=='BLOCKED'
    assert 'private-sentinel' not in str(probes.results)


def test_redis_probe_overrides_url_tls_downgrades_and_cleans_key(monkeypatch):
    import redis
    calls=[]
    class FakeRedis:
        connection_pool=SimpleNamespace(connection_kwargs={'ssl_cert_reqs':'none','ssl_check_hostname':False})
        def __enter__(self): return self
        def __exit__(self,*args): pass
        def ping(self): return True
        def set(self,key,value,ex): calls.append(('set',key,ex))
        def get(self,key): return b'probe'
        def delete(self,key): calls.append(('delete',key))
    fake=FakeRedis()
    monkeypatch.setattr(redis.Redis,'from_url',lambda *args,**kwargs:fake)
    monkeypatch.setenv('ROOT404_VERIFY_REDIS_URL','rediss://invalid.example?ssl_cert_reqs=none')
    probes.redis()
    assert fake.connection_pool.connection_kwargs['ssl_cert_reqs']=='required'
    assert fake.connection_pool.connection_kwargs['ssl_check_hostname'] is True
    assert calls[0][2]==30 and calls[-1][0]=='delete' and calls[0][1]==calls[-1][1]


def test_postgres_probe_refuses_non_verifying_tls_before_connection(monkeypatch):
    import psycopg2
    monkeypatch.setenv('ROOT404_VERIFY_DATABASE_URL','postgresql://test@invalid.example/db?sslmode=require')
    monkeypatch.setattr(psycopg2,'connect',lambda *a,**kw:pytest.fail('Non-verifying TLS accepted'))
    with pytest.raises(AssertionError): probes.postgres()


def test_public_proxy_probe_requires_https(monkeypatch):
    monkeypatch.setenv('ROOT404_VERIFY_PUBLIC_URL','http://invalid.example')
    with pytest.raises(AssertionError): probes.proxy()
