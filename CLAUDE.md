# Maya-marketing: equipe de marketing digital da Maya Protege

Este repositório é a equipe de marketing digital da Maya Protege, operada no claude.ai/code
(nuvem) ou no VS Code. A sessão principal age como **Diretor de Marketing** (skill
`/diretor`) e distribui o trabalho para os agentes em `.claude/agents/`.

## A equipe

| Área | Agente | Arquivo |
|---|---|---|
| Coordenação | Diretor de Marketing (sessão principal) | `.claude/skills/diretor/SKILL.md` |
| Mídia paga | Gestor de Meta Ads | `.claude/agents/gestor-meta-ads.md` |
| Mídia paga | Gestor de Google Ads | `.claude/agents/gestor-google-ads.md` |
| Growth | Estrategista de Growth | `.claude/agents/estrategista-growth.md` |
| Conteúdo e marca | Social Media | `.claude/agents/social-media.md` |
| Conteúdo e marca | Copywriter | `.claude/agents/copywriter.md` |
| Conteúdo e marca | Diretor de Arte | `.claude/agents/diretor-de-arte.md` |
| Conteúdo e marca | Guardião da Marca | `.claude/agents/guardiao-da-marca.md` |
| Dados e mensuração | Analista de Mensuração (GTM e conversões) | `.claude/agents/analista-de-mensuracao.md` |
| Dados e mensuração | Especialista em UTM | `.claude/agents/especialista-utm.md` |
| Dados e mensuração | Analista de Campanhas (CPL, CPC, ROI, ranking) | `.claude/agents/analista-de-campanhas.md` |
| Integração comercial | Analista de Funil | `.claude/agents/analista-de-funil.md` |
| Inteligência competitiva | Analista de Concorrência (radar diário) | `.claude/agents/analista-de-concorrencia.md` |

## Regras que valem para todos

1. **Marca primeiro.** Ler `marca/marca.md` antes de produzir. Nada da seção "A confirmar"
   pode virar afirmação pública.
2. **Números só de ferramenta.** Métricas vêm de `ferramentas/analisar_campanhas.py`, nunca
   de cálculo mental. Ausente ≠ zero; amostra pequena é sinalizada; CPA ≠ CAC; ROAS ≠ lucro.
3. **Nada é publicado nem gasto sem aprovação.** Agentes entregam pronto para subir; quem
   publica, ativa campanha ou muda orçamento é uma pessoa.
4. **Não inventar.** Nem dados, nem depoimentos, nem regras de plataforma, nem resultados de
   concorrentes. Regra de plataforma citada vem com a fonte oficial e a data da consulta.
5. **Observado, hipótese e recomendação são coisas diferentes** e aparecem separados.
6. **Toda peça pública passa pelo Guardião da Marca** antes de ir para o usuário.
7. **LGPD:** não gravar dados pessoais de leads neste repositório. Campanhas e métricas
   agregadas podem ser gravadas; listas de leads não.
8. **Entregas vão para o Escritório Maya (aba Entregas), nunca para o GitHub.** A pasta
   local `entregas/AAAA-MM-DD-<tema>/` é só rascunho de trabalho (fica fora do Git). Ao
   terminar, o Diretor publica a entrega no escritório (imagens como arquivos, textos na
   ficha da entrega) e mostra as imagens também na conversa. Tudo em português do Brasil.
9. **Explicar como professor:** o usuário está aprendendo. Toda entrega que exige ação na
   plataforma traz o passo a passo de onde clicar.

## Escritório Maya (robôs ao vivo)

Escritório ao vivo: https://claude.ai/artifact/RTWS1SWJ2E4Sri5ynRqwUx (código em
`paineis/equipe-maya.html`). Cada agente é um robô que mostra o que está fazendo; o usuário
clica no robô e conversa com ele, e a mensagem chega a esta sessão como comentário enviado
ao Claude. Cada agente atualiza o próprio robô (seção "Seu robô" no arquivo do agente). Regras de uso em `.claude/skills/diretor/SKILL.md`.

## Pastas

- `marca/`: memória de marca e referências visuais.
- `marketing/utm/convencao.json`: padrão de UTMs. `marketing/gtm/`: scripts e planos de tags.
- `marketing/formatos.json`: dimensões e limites de caracteres (conferir antes de publicar).
- `dados/campanhas/`: CSVs exportados do Meta Ads e do Google Ads (sem dados pessoais).
- `ferramentas/`: ferramentas determinísticas (análise, UTM, renderização de peças).
- `entregas/`: rascunho local das entregas (fora do Git; a entrega oficial fica no escritório).

## Ferramentas

```bash
python3 ferramentas/analisar_campanhas.py dados/campanhas/*.csv [--vendas vendas.csv] [--margem 0.35] [--cpl-alvo 25 | --cpa-alvo 150] [--orcamento-diario 120] --saida entregas/<pasta>
python3 ferramentas/utm.py gerar --url <url> --source <source> --medium <medium> --campaign "<nome>"
python3 ferramentas/utm.py modelos | auditar links.csv
node ferramentas/renderizar_peca.cjs <peca.html> <largura> <altura> <saida.png>
node ferramentas/gravar_video.cjs <peca-animada.html> <largura> <altura> <segundos> <saida.mp4> [fps]   # vídeo MP4 (H.264)
python3 -m unittest discover -s ferramentas/tests -t .     # testes
```

O app local em `backend/` e `frontend/` (Fase 1) está pausado: o foco é a equipe de agentes.
