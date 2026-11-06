---
name: utm
description: Gera ou audita links com UTM no padrão da Maya Protege (Meta, Google, Instagram, WhatsApp, e-mail, QR code). Atalho para o agente especialista-utm.
---

Para um link simples, gere direto com a ferramenta:
`python3 ferramentas/utm.py gerar --url <url> --source <source> --medium <medium> --campaign "<nome>" [--content <c>]`
e explique cada parâmetro em uma linha.

Para vários links, modelos para as plataformas ou auditoria de links existentes, acione o
subagente **especialista-utm** com o pedido completo.

Se o usuário não informar a URL de destino, pergunte. Nunca invente o domínio do site.
