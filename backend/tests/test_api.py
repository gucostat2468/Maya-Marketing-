def test_health(client):
    body = client.get("/api/health").json()
    assert body["status"] == "ok" and body["workspace"] == "real"


def test_system_reports_schema_and_fts5(client):
    body = client.get("/api/system").json()
    assert body["schema_revision"] == "0001_fundacao"
    assert body["fts5_available"] is True
    assert body["db_path"].endswith("maya.db")


def test_dashboard_without_data_never_shows_numbers(client):
    body = client.get("/api/dashboard/summary").json()
    assert body["coverage"]["has_data"] is False
    assert "Nenhuma integração foi autenticada" in body["coverage"]["message"]
    assert body["period"]["days"] == 30
    assert len(body["kpis"]) == 16
    for kpi in body["kpis"]:
        assert kpi["current"]["value"] is None
        assert kpi["current"]["status"] == "no_data"


def test_dashboard_period_and_comparison(client):
    body = client.get("/api/dashboard/summary?start=2026-10-01&end=2026-10-31").json()
    assert body["period"] == {"start": "2026-10-01", "end": "2026-10-31", "days": 31}
    assert body["comparison_period"] == {"start": "2026-08-31", "end": "2026-09-30", "days": 31}


def test_dashboard_rejects_invalid_period(client):
    assert client.get("/api/dashboard/summary?start=2026-10-10&end=2026-10-01").status_code == 422
    assert client.get("/api/dashboard/summary?start=2026-10-10").status_code == 422


def test_dashboard_echoes_filters(client):
    body = client.get("/api/dashboard/summary?platform=google_ads").json()
    assert body["filters"] == {"platform": "google_ads"}


def test_reference_seed_is_idempotent_and_has_no_secrets(client):
    from app.db.session import get_db
    from app.services.seed import seed_reference_data

    first = client.get("/api/integrations").json()
    db = next(get_db())
    seed_reference_data(db)
    db.close()
    second = client.get("/api/integrations").json()
    assert len(first) == len(second) > 0
    assert all(i["status"] != "connected" for i in second)
    assert not any("token" in key for item in second for key in item)


def test_modules_registry_is_honest(client):
    modules = client.get("/api/modules").json()
    assert len(modules) == 14
    statuses = {m["key"]: m["status"] for m in modules}
    assert statuses["settings"] == "available"
    assert statuses["leads"] == "planned"


def test_metric_definitions(client):
    defs = {d["key"]: d for d in client.get("/api/metrics/definitions").json()}
    assert defs["cpl"]["formula"] == "investimento ÷ leads"
    assert defs["cac"]["numerator"] == "acquisition_cost_total"
