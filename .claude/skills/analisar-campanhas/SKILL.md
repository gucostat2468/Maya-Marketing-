---
name: analisar-campanhas
description: Analisa campanhas do Meta Ads e do Google Ads (CSV exportado): investimento, CPC, CTR, CPL, CPA, ROAS, ROI e qual campanha performa melhor. Atalho para o agente analista-de-campanhas.
---

Acione o subagente **analista-de-campanhas** com:
- os arquivos indicados pelo usuário (ou todos os CSVs em `dados/campanhas/`);
- o período, a planilha de vendas e a margem, se o usuário informou;
- pasta de saída `entregas/<data de hoje>-analise-campanhas/`.

Se não houver nenhum CSV, não acione o agente: explique ao usuário como exportar os
relatórios (instruções na seção "Como orientar a exportação" de
`.claude/agents/analista-de-campanhas.md`) e onde colocá-los (`dados/campanhas/`, ou
anexando o arquivo na conversa).

Ao receber o resultado, apresente ao usuário o resumo executivo, o ranking com os empates
técnicos e as recomendações, e indique onde estão os arquivos.
