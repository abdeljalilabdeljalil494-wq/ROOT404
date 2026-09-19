"""Project catalogue + submission flow and validation."""
from __future__ import annotations

from sqlalchemy import func, select

from app.models import Submission
from tests.conftest import login_headers, make_user

PASSWORD = "S3cure-passw0rd!"


def _register_and_login(client, db_session, username: str):
    user = make_user(db_session, email=f"{username}@example.tn", username=username)
    return user, login_headers(client, user.email, PASSWORD)


def test_seeded_projects_are_listed(client):
    response = client.get("/api/projects")
    assert response.status_code == 200
    slugs = {p["slug"] for p in response.json()}
    assert slugs == {"libft", "ft_printf", "minishell"}
    for project in response.json():
        assert project["difficulty"] in {"easy", "medium", "hard"}
        assert project["xp_reward"] > 0


def test_project_detail_by_slug(client):
    response = client.get("/api/projects/libft")
    assert response.status_code == 200
    assert response.json()["title"].startswith("Libft")


def test_project_detail_unknown_slug_404(client):
    assert client.get("/api/projects/does-not-exist").status_code == 404


def test_submission_flow_roundtrip(client, db_session):
    user, headers = _register_and_login(client, db_session, "flowuser")
    response = client.post(
        "/api/projects/libft/submissions",
        json={"language": "c", "code": "int main(void){return 0;}"},
        headers=headers,
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["project_id"] and body["user_id"] == user.id
    assert body["status"] == "pending"
    assert "code" not in body  # read model must not echo source code

    stored = db_session.scalar(select(Submission).where(Submission.id == body["id"]))
    assert stored is not None and stored.code.startswith("int main")


def test_resubmission_updates_same_row(client, db_session):
    user, headers = _register_and_login(client, db_session, "resub")
    payload = {"language": "python", "code": "v1"}
    assert client.post("/api/projects/libft/submissions", json=payload, headers=headers).status_code == 201
    payload2 = {"language": "python", "code": "v2-better"}
    assert client.post("/api/projects/libft/submissions", json=payload2, headers=headers).status_code == 201

    rows = db_session.scalars(
        select(Submission).where(Submission.user_id == user.id)
    ).all()
    assert len(rows) == 1, "resubmission must UPDATE, not duplicate"
    assert rows[0].code == "v2-better"
    assert rows[0].status == "pending"


def test_submission_invalid_payloads(client, db_session):
    _, headers = _register_and_login(client, db_session, "invalid")
    cases = [
        {"language": "rust", "code": "fn main(){}"},   # unsupported language
        {"language": "python", "code": ""},            # empty code
        {"language": "python"},                        # missing code
        {"language": "python", "code": "x" * 100_001}, # over size cap
    ]
    for payload in cases:
        response = client.post("/api/projects/libft/submissions", json=payload, headers=headers)
        assert response.status_code == 422, f"{payload['language']}: {response.text}"
    assert db_session.scalar(select(func.count()).select_from(Submission)) == 0


def test_submission_to_unknown_project_404(client, db_session):
    _, headers = _register_and_login(client, db_session, "orphan")
    response = client.post(
        "/api/projects/nope/submissions", json={"language": "python", "code": "x"}, headers=headers
    )
    assert response.status_code == 404


def test_submissions_of_unpublished_project_hidden(client, db_session):
    from app.models import Project

    _, headers = _register_and_login(client, db_session, "hidden")
    db_session.add(Project(slug="secret", title="WIP", is_published=False))
    db_session.commit()
    assert client.get("/api/projects/secret").status_code == 404
    listed = {p["slug"] for p in client.get("/api/projects").json()}
    assert "secret" not in listed
