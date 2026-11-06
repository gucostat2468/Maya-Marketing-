"""Dados de REFERÊNCIA (catálogo de plataformas e conectores).

Não são dados de marketing: nenhum número, campanha ou lead é criado aqui.
A operação é idempotente: rodar várias vezes não duplica registros.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Integration, Platform

PLATFORMS = [
    ("google_ads", "Google Ads", "ads"),
    ("meta_ads", "Meta Ads (Facebook e Instagram)", "ads"),
    ("instagram", "Instagram", "social"),
    ("facebook", "Facebook", "social"),
    ("ga4", "Google Analytics 4", "analytics"),
    ("gtm", "Google Tag Manager", "analytics"),
    ("crm", "CRM (fornecedor a definir)", "crm"),
]

# (code, name, platform, auth_type, planned_phase, supports_csv, notes)
INTEGRATIONS = [
    (
        "google_ads_csv",
        "Google Ads — importação de relatório CSV",
        "google_ads",
        "csv",
        2,
        True,
        "Primeira forma de trazer dados do Google Ads, antes da API oficial.",
    ),
    (
        "google_ads_api",
        "Google Ads API (OAuth 2.0)",
        "google_ads",
        "oauth2",
        4,
        False,
        "Exige developer token aprovado pelo Google, OAuth client e autorização explícita.",
    ),
    (
        "meta_ads_csv",
        "Meta Ads — importação de relatório CSV",
        "meta_ads",
        "csv",
        2,
        True,
        "Exportação do Gerenciador de Anúncios.",
    ),
    (
        "meta_marketing_api",
        "Meta Marketing API",
        "meta_ads",
        "oauth2",
        4,
        False,
        "Exige app na Meta for Developers e permissões ads_read.",
    ),
    (
        "instagram_insights",
        "Instagram Insights (Graph API)",
        "instagram",
        "oauth2",
        4,
        False,
        "Exige conta profissional vinculada a uma Página do Facebook.",
    ),
    ("social_csv", "Métricas sociais — importação CSV", "instagram", "csv", 2, True, None),
    ("ga4_api", "Google Analytics 4 Data API", "ga4", "oauth2", 4, False, None),
    (
        "leads_csv",
        "Leads — importação de planilha",
        None,
        "csv",
        3,
        True,
        "Planilhas de leads com minimização de dados pessoais.",
    ),
    (
        "crm_adapter",
        "Conector de CRM",
        "crm",
        "none",
        7,
        False,
        "Fornecedor ainda não definido. Nenhum endpoint será implementado antes da definição.",
    ),
]


def seed_reference_data(db: Session) -> None:
    existing = {p.code: p for p in db.scalars(select(Platform))}
    for code, name, kind in PLATFORMS:
        if code not in existing:
            platform = Platform(code=code, name=name, kind=kind)
            db.add(platform)
            existing[code] = platform
    db.flush()

    known = set(db.scalars(select(Integration.code)))
    for code, name, platform, auth, phase, csv, notes in INTEGRATIONS:
        if code in known:
            continue
        db.add(
            Integration(
                code=code,
                name=name,
                platform_id=existing[platform].id if platform else None,
                auth_type=auth,
                planned_phase=phase,
                supports_csv=csv,
                status="planned",
                notes=notes,
            )
        )
    db.commit()
