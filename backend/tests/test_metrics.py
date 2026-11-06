from decimal import Decimal

from app.domain.metrics import CATALOG, MetricStatus, compare, compute, ratio, round_money


def test_example_from_brief_campaign_a_vs_b():
    """Exemplo do briefing: B tem CPL parecido, mas eficiência comercial muito superior."""
    a = compute({"spend": 100, "leads": 50, "sales": 3})
    b = compute({"spend": 30, "leads": 20, "sales": 15})
    assert a["cpl"].value == Decimal(2)
    assert b["cpl"].value == Decimal("1.5")
    assert a["lead_to_sale_rate"].value == Decimal("0.06")
    assert b["lead_to_sale_rate"].value == Decimal("0.75")
    assert round_money(a["cpa"].value) == Decimal("33.33")
    assert b["cpa"].value == Decimal(2)


def test_missing_input_is_no_data_not_zero():
    result = compute({"spend": 100})
    assert result["cpl"].status == MetricStatus.NO_DATA
    assert result["cpl"].value is None
    assert result["cpl"].missing_inputs == ["leads"]
    assert result["leads"].status == MetricStatus.NO_DATA


def test_measured_zero_is_kept_as_zero():
    result = compute({"leads": 0})
    assert result["leads"].status == MetricStatus.OK
    assert result["leads"].value == Decimal(0)


def test_zero_denominator_is_undefined():
    result = compute({"spend": 100, "leads": 0})
    assert result["cpl"].status == MetricStatus.UNDEFINED
    assert result["cpl"].value is None
    assert "zero" in result["cpl"].reason


def test_cac_is_not_cpa():
    """Sem custo total de aquisição, o CAC não é calculado (não usa só a mídia)."""
    result = compute({"spend": 100, "sales": 4})
    assert result["cpa"].value == Decimal(25)
    assert result["cac"].status == MetricStatus.NO_DATA
    assert result["cac"].missing_inputs == ["acquisition_cost_total"]
    full = compute({"spend": 100, "acquisition_cost_total": 260, "sales": 4})
    assert full["cac"].value == Decimal(65)


def test_roas_and_caveat():
    result = compute({"revenue": 500, "spend": 200})
    assert result["roas"].value == Decimal("2.5")
    assert "lucro" in CATALOG["roas"].caveat


def test_cpm_multiplier_and_traceability():
    result = ratio(CATALOG["cpm"], 50, 10_000)
    assert result.value == Decimal(5)
    assert result.numerator == Decimal(50) and result.denominator == Decimal(10_000)


def test_float_inputs_do_not_leak_binary_errors():
    result = compute({"spend": 0.1, "clicks": 0.3 * 10})  # 0.1 / 3.0
    assert str(result["cpc"].value).startswith("0.0333")


def test_compare_periods():
    cur, prev = compute({"leads": 120}), compute({"leads": 100})
    change = compare(cur["leads"], prev["leads"])
    assert change.absolute == Decimal(20) and change.relative == Decimal("0.2")
    assert compare(cur["leads"], compute({})["leads"]).status == MetricStatus.NO_DATA
    zero = compare(cur["leads"], compute({"leads": 0})["leads"])
    assert zero.absolute == Decimal(120) and zero.relative is None
