import pytest


@pytest.fixture(autouse=True)
def isolated_replay_store(monkeypatch,tmp_path):
    monkeypatch.setenv('EXECUTOR_REPLAY_DB',str(tmp_path/'claims.sqlite'))
