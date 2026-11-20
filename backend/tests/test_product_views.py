from app.core.database import SessionLocal
from app.models.user import User
from test_rc_workflows import account, client


def test_search_requires_both_public_optins_and_excludes_inactive_profiles():
    owner, headers = account()
    other, _ = account()
    with SessionLocal() as db:
        user = db.get(User, other)
        user.username = 'uniquefindableprofile'
        user.directory_visible = True
        user.public_profile = False
        db.commit()
    assert client.get('/api/search?q=uniquefindable',headers=headers).json()['users'] == []
    with SessionLocal() as db:
        db.get(User,other).public_profile = True; db.commit()
    rows=client.get('/api/search?q=uniquefindable',headers=headers).json()['users']
    assert [row['username'] for row in rows] == ['uniquefindableprofile']
    assert 'email' not in rows[0]
    with SessionLocal() as db:
        db.get(User,other).is_active = False; db.commit()
    assert client.get('/api/search?q=uniquefindable',headers=headers).json()['users'] == []
    assert client.get('/api/portfolio/uniquefindableprofile').status_code == 404
    assert client.get('/api/search',params={'q':'%'},headers=headers).json()['users'] == []


def test_unknown_coalition_filter_never_silently_returns_global_leaderboard():
    assert client.get('/api/leaderboard/?coalition=does-not-exist').json() == []
