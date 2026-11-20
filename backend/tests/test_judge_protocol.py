"""Actual API transport validation with mocked worker HTTP, not live execution."""
import json
import uuid
import httpx
import pytest
from fastapi import HTTPException
from app.core.config import settings
from app.core.judge_protocol import sign
from app.services import judge


def configure(monkeypatch,handler):
    monkeypatch.setattr(settings,'JUDGE_ENABLED',True)
    monkeypatch.setattr(settings,'JUDGE_EXPECTED_IMAGE','root404/jobs@sha256:'+'a'*64)
    monkeypatch.setattr(settings,'JUDGE_URL','https://worker.invalid')
    monkeypatch.setattr(settings,'JUDGE_SHARED_SECRET','s'*64)
    real=httpx.Client
    monkeypatch.setattr(httpx,'Client',lambda **kwargs:real(transport=httpx.MockTransport(handler),**kwargs))


def receipt(request):
    body=json.loads(request.content)
    result={'status':'success','output':'42\n','error':'','exit_code':0,'execution_time':.1}
    evidence={'image':'root404/jobs@sha256:'+'a'*64,'phases':[{'phase':'run',
        'container':'root404-job-'+'b'*32+'-run','exit_code':0,'oom_killed':False,'timed_out':False,'output_limited':False}]}
    return sign('s'*64,request.headers['x-root404-request-id'],body,result,evidence)


def test_backend_accepts_bound_receipt_and_rejects_same_receipt_for_fresh_request(monkeypatch):
    saved=[]
    def handler(request):
        assert request.url.path=='/v2/execute'
        if not saved: saved.append(receipt(request))
        return httpx.Response(200,json=saved[0])
    configure(monkeypatch,handler)
    assert judge._execute({'main.py':'print(42)'},'python')['output']=='42\n'
    with pytest.raises(HTTPException) as failure: judge._execute({'main.py':'print(42)'},'python')
    assert failure.value.status_code==503


@pytest.mark.parametrize('attack',['unsigned','forged','wrong_job','contradictory_state'])
def test_backend_does_not_accept_forged_or_merely_signed_results(monkeypatch,attack):
    def handler(request):
        raw=receipt(request)
        if attack=='unsigned': return httpx.Response(200,json=raw['result'])
        if attack=='forged': raw['result']['output']='FORGED'
        if attack=='wrong_job': raw['request_digest']='f'*64
        if attack=='contradictory_state':
            body=json.loads(request.content)
            raw['evidence']['phases'][0]['exit_code']=7
            raw=sign('s'*64,raw['request_id'],body,raw['result'],raw['evidence'])
        return httpx.Response(200,json=raw)
    configure(monkeypatch,handler)
    with pytest.raises(HTTPException) as failure: judge._execute({'main.py':'print(42)'},'python')
    assert failure.value.status_code==503
