import sqlite3


def test_backup_create_list_and_restore(client):
    created = client.post("/api/backups")
    assert created.status_code == 201
    name = created.json()["name"]
    assert any(b["name"] == name for b in client.get("/api/backups").json())

    # Altera o banco depois do backup...
    from app.core.config import get_settings

    db_path = get_settings().db_path
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO app_settings (key, value, created_at, updated_at) "
            "VALUES ('marcador', '1', '2026-01-01', '2026-01-01')"
        )
    conn.close()

    # ...e restaura: o marcador some, e um backup de segurança é criado.
    resp = client.post(f"/api/backups/{name}/restore", json={"confirmation": "RESTAURAR"})
    assert resp.status_code == 200, resp.text
    assert resp.json()["safety_backup"].endswith("-pre-restauracao.db")
    conn = sqlite3.connect(db_path)
    assert conn.execute("SELECT count(*) FROM app_settings WHERE key='marcador'").fetchone()[0] == 0
    conn.close()
    assert client.get("/api/health").status_code == 200
    actions = [a["action"] for a in client.get("/api/audit").json()]
    assert "backup.restored" in actions
    # A trilha de auditoria sobrevive à restauração (o registro de criação continua lá).
    assert "backup.created" in actions


def test_restore_requires_confirmation(client):
    name = client.post("/api/backups").json()["name"]
    resp = client.post(f"/api/backups/{name}/restore", json={"confirmation": "sim"})
    assert resp.status_code == 422


def test_restore_rejects_path_traversal(client):
    resp = client.post("/api/backups/..%2F..%2Fmaya.db/restore", json={"confirmation": "RESTAURAR"})
    assert resp.status_code in (400, 404)
    resp = client.post("/api/backups/qualquer.db/restore", json={"confirmation": "RESTAURAR"})
    assert resp.status_code == 400
