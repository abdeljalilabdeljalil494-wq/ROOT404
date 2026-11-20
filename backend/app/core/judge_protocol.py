"""Pure v2 wire contract, shared by API verifier and trusted host dispatcher.

HMAC binds a receipt to ONE fresh request; it does NOT attest a trusted execution.
Secrets and this receipt writer are never copied into the learner image.
"""
import hashlib
import hmac
import json
import time
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


class Result(BaseModel):
    model_config = ConfigDict(extra='forbid',strict=True,allow_inf_nan=False)
    status: Literal['success','compilation_error','runtime_error','timeout','memory_limit','output_limit']
    output: str = Field(max_length=65536)
    error: str = Field(max_length=65536)
    exit_code: int | None
    execution_time: float = Field(ge=0,le=120)

    @model_validator(mode='after')
    def consistent(self):
        if self.status=='success' and self.exit_code!=0: raise ValueError('Invalid success')
        return self


class Observation(BaseModel):
    model_config = ConfigDict(extra='forbid',strict=True)
    phase: Literal['compile','run']
    container: str = Field(pattern=r'^root404-job-[a-f0-9]{32}-(compile|run)$')
    exit_code: int = Field(ge=0,le=255)
    oom_killed: bool
    timed_out: bool
    output_limited: bool

    @model_validator(mode='after')
    def matching_phase(self):
        if not self.container.endswith('-'+self.phase): raise ValueError('Observation phase mismatch')
        return self

    def status(self):
        return ('memory_limit' if self.oom_killed else 'timeout' if self.timed_out or self.exit_code==152
                else 'output_limit' if self.output_limited else 'success' if self.exit_code==0
                else 'compilation_error' if self.phase=='compile' else 'runtime_error')


class Evidence(BaseModel):
    model_config = ConfigDict(extra='forbid',strict=True)
    image: str = Field(pattern=r'^[a-zA-Z0-9][a-zA-Z0-9./:_-]*@sha256:[a-f0-9]{64}$')
    phases: list[Observation] = Field(min_length=1,max_length=2)


class Envelope(BaseModel):
    model_config = ConfigDict(extra='forbid',strict=True)
    version: Literal[2]
    request_id: str = Field(pattern=r'^[a-f0-9]{32}$')
    request_digest: str = Field(pattern=r'^[a-f0-9]{64}$')
    issued_at: int
    result: Result
    evidence: Evidence
    signature: str = Field(pattern=r'^[a-f0-9]{64}$')


def authenticate(secret, payload):
    key=hmac.digest(secret.encode(),b'ROOT404-execution-receipt-v2','sha256')
    return hmac.new(key,canonical(payload),hashlib.sha256).hexdigest()


def sign(secret, request_id, job, result, evidence, now=None):
    payload={'version':2,'request_id':request_id,'request_digest':digest(job),
             'issued_at':int(time.time() if now is None else now),
             'result':Result.model_validate(result).model_dump(),'evidence':Evidence.model_validate(evidence).model_dump()}
    return {**payload,'signature':authenticate(secret,payload)}


def verify(secret, request_id, job, raw, now=None, expected_image=None):
    envelope=Envelope.model_validate(raw)
    payload=envelope.model_dump(exclude={'signature'})
    if not hmac.compare_digest(authenticate(secret,payload),envelope.signature): raise ValueError('Invalid receipt authentication')
    if envelope.request_id!=request_id or envelope.request_digest!=digest(job): raise ValueError('Receipt belongs to another request')
    if abs(int(time.time() if now is None else now)-envelope.issued_at)>30: raise ValueError('Stale receipt')
    if expected_image is not None and envelope.evidence.image!=expected_image: raise ValueError('Unapproved toolchain image')
    phases=envelope.evidence.phases
    if len({item.container.rsplit('-',1)[0] for item in phases})!=1: raise ValueError('Mixed job observations')
    names=[item.phase for item in phases]
    if job['language'] in {'c','cpp','c++'}:
        if names not in [['compile'],['compile','run']]: raise ValueError('Missing compilation observation')
        if len(phases)==1 and phases[0].status()=='success': raise ValueError('Missing execution observation')
    elif names!=['run']: raise ValueError('Invalid runtime observation')
    if any(item.status()!='success' for item in phases[:-1]): raise ValueError('Ran after failed compilation')
    if envelope.result.status!=phases[-1].status() or envelope.result.exit_code!=phases[-1].exit_code:
        raise ValueError('Receipt disagrees with independently observed state')
    return envelope.result.model_dump()
