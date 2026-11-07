"""Funções estatísticas compartilhadas pelas ferramentas."""

from __future__ import annotations

import math


def poisson_ci(count: int, z: float = 1.96) -> tuple[float, float]:
    """Intervalo de 95% para uma contagem (aproximação de Byar). Ex.: nº de leads."""
    if count <= 0:
        upper = (count + 1) * (1 - 1 / (9 * (count + 1)) + z / (3 * math.sqrt(count + 1))) ** 3
        return 0.0, upper
    lower = count * (1 - 1 / (9 * count) - z / (3 * math.sqrt(count))) ** 3
    upper = (count + 1) * (1 - 1 / (9 * (count + 1)) + z / (3 * math.sqrt(count + 1))) ** 3
    return lower, upper
