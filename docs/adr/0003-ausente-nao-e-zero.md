# ADR 0003: Indicadores distinguem "sem dados", "zero" e "não calculável"

- **Status:** aceita
- **Data:** 2026-11-06

## Contexto

Dashboards de marketing costumam exibir "R$ 0,00" quando não há dados, o que leva a decisões
erradas (ex.: "o CPL caiu a zero").

## Decisão

Todo indicador tem um status: `ok` (valor calculado), `no_data` (falta algum insumo) ou
`undefined` (insumos existem, mas o denominador é zero). Valores monetários usam `Decimal`.
A resposta da API traz fórmula, numerador, denominador e insumos ausentes, e a interface
exibe "Sem dados" ou "Não calculável", nunca 0.

## Consequências

O código que agrega dados (Fase 2) **deve** devolver `None` quando não houver fonte para um
período ou filtro, e `0` só quando a fonte reportou zero. Isso é coberto por testes.
