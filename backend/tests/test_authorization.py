"""Authorization: anonymous rejection + cross-user private data isolation."""
from __future__ import annotations

from tests.conftest import login_headers, make_user


def test_protected_endpoints_reject_anonymous(client):
    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/api/submissions/mine").status_code == 401
    assert client.post(
        "/api/projects/libft/submissions", json={"language": "python", "code": "print(1)"}
    ).status_code == 401


def test_invalid_token_rejected_on_protected_endpoint(client):
    response = client.get("/api/submissions/mine", headers={"Authorization": "Bearer f.k.e"})
    assert response.status_code == 401


def test_user_cannot_read_another_users_submission(client, db_session):
    alice = make_user(db_session, email="alice@example.tn", username="alice")
    bob = make_user(db_session, email="bob@example.tn", username="bob")

    create = client.post(
        "/api/projects/libft/submissions",
        json={"language": "c", "code": "int main(void){return 0;}"},
        headers=login_headers(client, alice.email, "S3cure-passw0rd!"),
    )
    assert create.status_code == 201
    submission_id = create.json()["id"]

    #: Bob addresses Alice's submission directly -> 404, not 403 (no leak).
    bob_headers = login_headers(client, bob.email, "S3cure-passw0rd!")
    stolen = client.get(f"/api/submissions/{submission_id}", headers=bob_headers)
    assert stolen.status_code == 404

    #: Alice still sees her own.
    alice_headers = login_headers(client, alice.email, "S3cure-passw0rd!")
    own = client.get(f"/api/submissions/{submission_id}", headers=alice_headers)
    assert own.status_code == 200
    assert own.json()["user_id"] == alice.id


def test_submissions_mine_only_returns_own(client, db_session):
    alice = make_user(db_session, email="alice2@example.tn", username="alice2")
    bob = make_user(db_session, email="bob2@example.tn", username="bob2")
    alice_headers = login_headers(client, alice.email, "S3cure-passw0rd!")
    bob_headers = login_headers(client, bob.email, "S3cure-passw0rd!")

    client.post(
        "/api/projects/libft/submissions",
        json={"language": "python", "code": "print('alice')"},
        headers=alice_headers,
    )
    client.post(
        "/api/projects/ft_printf/submissions",
        json={"language": "cpp", "code": "int main(){return 0;}"},
        headers=bob_headers,
    )

    alice_rows = client.get("/api/submissions/mine", headers=alice_headers).json()
    bob_rows = client.get("/api/submissions/mine", headers=bob_headers).json()
    assert [r["project_id"] for r in alice_rows] != []
    assert all(r["user_id"] == alice.id for r in alice_rows)
    assert all(r["user_id"] == bob.id for r in bob_rows)
    assert {r["id"] for r in alice_rows}.isdisjoint({r["id"] for r in bob_rows})
