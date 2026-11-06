# Guia de UTMs pronto para colar: Maya Protege®

Data: 2026-11-06 · Preparado pelo Especialista em UTM · Fonte do padrão: `marketing/utm/convencao.json`

> **Site oficial:** todos os links deste guia usam `https://mayaprotege.com.br/` (sem `www`,
> como aparece no site), confirmado em `marca/marca.md`, seção 6. O formulário de lead fica
> na página inicial, por isso os links apontam para ela.
>
> **Páginas internas:** se quiser mandar a pessoa para uma página específica (ex.: a página
> de um plano), **abra o site e confira o caminho exato** antes de gerar o link. Esses
> caminhos não foram confirmados e não aparecem neste guia.

---

## 1. O que é UTM e por que importa

1. UTM é uma "etiqueta" que vai no fim do link, depois do `?`, e diz de onde a pessoa veio.
2. Exemplo: `?utm_source=instagram&utm_medium=organic_social` = veio do Instagram, de post orgânico.
3. O Google Analytics 4 (GA4) lê essas etiquetas e separa as visitas e os leads por canal.
4. Sem UTM, ou com UTM bagunçada ("Instagram", "instagram", "IG"), o mesmo canal vira três e parte do tráfego cai em "Unassigned" (sem origem).
5. Com UTM certa, dá para saber qual anúncio, post ou panfleto trouxe cada lead e onde vale investir.

As 5 etiquetas que usamos:

| Parâmetro | Responde | Exemplo |
|---|---|---|
| `utm_source` | Qual site/plataforma? | `instagram`, `google`, `whatsapp` |
| `utm_medium` | Que tipo de tráfego? | `paid_social`, `cpc`, `email`, `offline` |
| `utm_campaign` | Qual campanha? | `leads-plano-familiar-sp-202611` |
| `utm_content` | Qual peça/anúncio? | `link-bio`, `panfleto` |
| `utm_term` | Qual público/palavra-chave? | nome do conjunto ou palavra buscada |

---

## 2. Meta Ads (Facebook e Instagram)

### Texto exato para colar

Saída de `python3 ferramentas/utm.py modelos`:

```
utm_source={{site_source_name}}&utm_medium=paid_social&utm_campaign={{campaign.name}}&utm_content={{ad.name}}&utm_term={{adset.name}}&utm_id={{campaign.id}}
```

Cole **exatamente assim**, sem `?` no começo e sem espaços. A Meta troca o que está entre
`{{ }}` pelo valor real no momento do clique. Assim você não digita UTM à mão em cada anúncio.

### Onde clicar (passo a passo)

1. Abra o **Gerenciador de Anúncios** da Meta.
2. Entre na campanha e depois no **conjunto de anúncios**.
3. Clique no **anúncio** (nível mais baixo) e em **Editar**.
4. Role a tela até a seção **Rastreamento**.
5. No campo **Parâmetros de URL**, cole o texto acima. (Se houver o botão "Criar um parâmetro de URL", você pode colar o texto direto no campo, sem usar o construtor.)
6. Confira se o campo **Site / URL do site** tem o link da página de destino **sem UTM** (a Meta junta os parâmetros sozinha).
7. Clique em **Publicar** só depois da aprovação de quem responde pela verba (regra da equipe: nada é publicado sem aprovação).
8. Repita em cada anúncio. Dica: ao duplicar um anúncio, o campo vem preenchido; confira mesmo assim.

### O que cada parâmetro dinâmico vira

| No texto colado | Vira | Exemplo do que aparece no GA4 |
|---|---|---|
| `{{site_source_name}}` | Onde o anúncio foi exibido | `fb` (Facebook), `ig` (Instagram), `msg` (Messenger), `an` (Audience Network) |
| `paid_social` (fixo) | Tipo de tráfego: mídia paga em rede social | `paid_social` |
| `{{campaign.name}}` | Nome da **campanha** | `leads-plano-familiar-sp-202611` |
| `{{ad.name}}` | Nome do **anúncio** | `video-30s-v1` |
| `{{adset.name}}` | Nome do **conjunto de anúncios** | `sp-25-45-interesses` |
| `{{campaign.id}}` | Número da campanha na Meta | `120210000000000000` |

**Importante:** como os nomes viram UTM, **nomeie campanha, conjunto e anúncio no padrão da
seção 5** (minúsculas, sem acento, hífen no lugar de espaço). Se a campanha se chamar
"Campanha Novembro!!", é isso que vai aparecer no relatório.

Os códigos `fb` e `ig` são reconhecidos pelo GA4 como redes sociais, então o tráfego cai em
"Paid Social" mesmo não sendo `facebook`/`instagram` por extenso.

---

## 3. Google Ads

### Texto exato para colar

Saída de `python3 ferramentas/utm.py modelos`:

```
utm_source=google&utm_medium=cpc&utm_campaign={_campanha}&utm_content={creative}&utm_term={keyword}&utm_id={campaignid}
```

### Passo 1: confirmar a codificação automática (gclid)

O Google Ads põe no link um código chamado **gclid**, que liga o clique ao GA4 e às
conversões. **Ele precisa continuar ligado.** As UTMs entram junto, não no lugar dele.

1. No Google Ads, clique em **Administrador** (ícone de engrenagem).
2. Vá em **Configurações da conta**.
3. Abra **Codificação automática** e confirme que está **ativada**. Se estiver desligada, marque e salve.

### Passo 2: colar o sufixo no nível da campanha

1. Abra a **campanha** e clique em **Configurações**.
2. Clique em **Configurações adicionais** e depois em **Opções de URL da campanha**.
3. No campo **Sufixo do URL final**, cole o texto acima (sem `?` no começo).
4. **Não salve ainda:** primeiro crie o parâmetro personalizado do passo 3, na mesma tela.

### Passo 3: criar o parâmetro personalizado `{_campanha}`

`{_campanha}` **não** é um código pronto do Google. É um **parâmetro personalizado**: um
"apelido" que você cria e ao qual dá o valor que quiser. Usamos isso para o `utm_campaign`
sair com o nome no padrão da Maya, sem depender do nome que aparece na interface.

1. Ainda em **Opções de URL da campanha**, procure **Parâmetros personalizados**.
2. Clique para adicionar um parâmetro.
3. No campo do **nome**, digite `_campanha` (com o sublinhado na frente; o Google coloca as chaves sozinho).
4. No campo do **valor**, digite o nome da campanha no padrão da seção 5, por exemplo `leads-plano-familiar-sp-202611` (o `sp` é só exemplo de público/região).
5. Clique em **Salvar**.
6. Cada campanha tem o seu próprio valor de `_campanha`. Ao criar uma campanha nova, repita os passos 2 e 3.

Se o parâmetro não for criado, o link sai com `utm_campaign=` vazio e a campanha fica sem nome no GA4.

### Passo 4: testar

Ainda em **Opções de URL**, use **Testar** (quando disponível) ou, depois de salvo, abra a
visualização do anúncio e copie o link: ele deve terminar com `utm_campaign=` seguido do
nome no padrão.

### O que cada parâmetro vira

| No texto colado | Vira |
|---|---|
| `google` e `cpc` (fixos) | Source e medium: o GA4 classifica como "Paid Search" |
| `{_campanha}` | O valor que você digitou no parâmetro personalizado |
| `{creative}` | Número (ID) do anúncio que foi clicado |
| `{keyword}` | Palavra-chave que acionou o anúncio (vazio em Display/YouTube/PMax, isso é normal) |
| `{campaignid}` | Número (ID) da campanha no Google Ads |

---

## 4. Links manuais (bio, WhatsApp, e-mail, QR code)

Aqui não existe parâmetro dinâmico: o link é gerado uma vez e colado. **Todos os links abaixo
saíram da ferramenta** (`python3 ferramentas/utm.py gerar`), com o site oficial
`https://mayaprotege.com.br/` e a campanha de exemplo `leads-plano-familiar-geral-202611`.
Para outra campanha ou outro plano, gere de novo com a ferramenta trocando o `--campaign`,
nunca editando o link à mão.

| Onde usar | Link final | source | medium | campaign | content |
|---|---|---|---|---|---|
| Instagram: link da bio | `https://mayaprotege.com.br/?utm_source=instagram&utm_medium=organic_social&utm_campaign=leads-plano-familiar-geral-202611&utm_content=link-bio` | instagram | organic_social | leads-plano-familiar-geral-202611 | link-bio |
| Instagram: link nos stories | `https://mayaprotege.com.br/?utm_source=instagram&utm_medium=organic_social&utm_campaign=leads-plano-familiar-geral-202611&utm_content=stories-link` | instagram | organic_social | leads-plano-familiar-geral-202611 | stories-link |
| Facebook: post orgânico | `https://mayaprotege.com.br/?utm_source=facebook&utm_medium=organic_social&utm_campaign=leads-plano-familiar-geral-202611&utm_content=post-feed` | facebook | organic_social | leads-plano-familiar-geral-202611 | post-feed |
| LinkedIn: post orgânico | `https://mayaprotege.com.br/?utm_source=linkedin&utm_medium=organic_social&utm_campaign=leads-plano-familiar-geral-202611&utm_content=post-perfil` | linkedin | organic_social | leads-plano-familiar-geral-202611 | post-perfil |
| WhatsApp: mensagem de atendimento | `https://mayaprotege.com.br/?utm_source=whatsapp&utm_medium=referral&utm_campaign=leads-plano-familiar-geral-202611&utm_content=mensagem-atendimento` | whatsapp | referral | leads-plano-familiar-geral-202611 | mensagem-atendimento |
| E-mail: botão principal | `https://mayaprotege.com.br/?utm_source=email&utm_medium=email&utm_campaign=leads-plano-familiar-geral-202611&utm_content=botao-principal` | email | email | leads-plano-familiar-geral-202611 | botao-principal |
| QR code: panfleto impresso | `https://mayaprotege.com.br/?utm_source=qrcode&utm_medium=offline&utm_campaign=leads-plano-familiar-geral-202611&utm_content=panfleto` | qrcode | offline | leads-plano-familiar-geral-202611 | panfleto |
| Parceiro/indicação | `https://mayaprotege.com.br/?utm_source=parceiro&utm_medium=referral&utm_campaign=leads-plano-familiar-geral-202611&utm_content=nome-do-parceiro` | parceiro | referral | leads-plano-familiar-geral-202611 | nome-do-parceiro |

Observações:

- **WhatsApp:** a UTM vai no link **do site** que você envia na conversa. Link de abrir
  conversa (`wa.me/...`) não leva a pessoa ao site, então não registra UTM no GA4 (o mesmo
  vale para o botão de WhatsApp do site: ele não precisa de UTM, e por ser link interno do
  próprio site não deve levar UTM). Usamos
  `referral` porque a convenção não tem um medium próprio para mensageiros; se a equipe
  quiser separar WhatsApp como canal, isso deve ser proposto como inclusão na convenção.
- **QR code:** sempre `utm_medium=offline`. Esse medium não faz parte dos canais padrão do
  GA4, então ele **pode aparecer como "Unassigned"** nos relatórios de canal; a origem
  continua visível nos relatórios por source/medium. O Analista de Mensuração pode criar um
  grupo de canais personalizado para "Offline". A criação de mediums próprios para WhatsApp e
  QR code na convenção **aguarda decisão** e não foi feita. Gere o QR code a partir do link **completo**
  (com as UTMs) e teste lendo com o celular antes de imprimir.
- **Bio do Instagram:** links longos funcionam normalmente na bio; não use encurtador sem
  testar se ele mantém as UTMs.
- Para cada peça diferente, mude só o `--content` (ex.: `panfleto-evento`, `cartao-visita`).

Como gerar um link novo (exemplo do QR code):

```bash
python3 ferramentas/utm.py gerar --url https://mayaprotege.com.br/ --source qrcode --medium offline --campaign "leads-plano-familiar-geral-202611" --content panfleto
```

Se você digitar algo fora do padrão, a ferramenta recusa e mostra as opções válidas. Teste real:

```
$ python3 ferramentas/utm.py gerar --url https://mayaprotege.com.br/ --source IG --medium social --campaign x
Erro: utm_source 'ig' fora do padrão. Use: facebook, instagram, google, youtube, whatsapp, email, linkedin, parceiro, qrcode
```

---

## 5. Padrão de nome de campanha

Formato da convenção:

```
<objetivo>-<produto>-<publico>-<aaaamm>
```

- **objetivo:** o que a campanha quer (`leads`, `remarketing`, `reconhecimento`...).
- **produto:** o plano anunciado, conforme `marca/marca.md`, seção 2: `plano-serenidade`, `plano-familiar`, `plano-familiar-plus` ou `plano-familiar-premium` (use `planos` quando a peça falar de todos).
- **publico:** quem é o alvo ou a região (`sp`, `familias`, `visitantes-site`, `geral`...). Os exemplos com `sp` são **só ilustração**: use a região ou o público real da campanha.
- **aaaamm:** ano e mês de início (`202611` = novembro de 2026).

Regras: tudo minúsculo, sem acento, sem espaço, palavras separadas por hífen.

| Plano | Exemplo de nome (validado pela ferramenta) |
|---|---|
| Familiar | `leads-plano-familiar-sp-202611` |
| Familiar Plus | `remarketing-plano-familiar-plus-visitantes-site-202612` |
| Serenidade | `reconhecimento-plano-serenidade-familias-202701` |
| Familiar Premium | `leads-plano-familiar-premium-sp-202611` |

Esse mesmo nome vai no nome da campanha da Meta (vira `{{campaign.name}}`) e no
parâmetro `_campanha` do Google.

---

## 6. Checklist: 6 erros comuns

- [ ] **1. Maiúsculas ou acentos.** `Instagram` e `instagram` viram duas origens diferentes no GA4. Use sempre minúsculas e sem acento (a ferramenta já corrige).
- [ ] **2. Source ou medium fora do padrão.** `ig`, `social`, `pago`, `zap`... quebram os relatórios e mandam tráfego para "Unassigned". Use só os valores de `marketing/utm/convencao.json`. Precisa de um novo? Proponha a inclusão na convenção, não use avulso.
- [ ] **3. UTM em link interno do site.** Nunca coloque UTM em botões, menus ou banners que levam de uma página do site para outra: isso reinicia a sessão e apaga a origem real do visitante.
- [ ] **4. Faltar `utm_campaign` (ou deixar vazio).** As três obrigatórias são `utm_source`, `utm_medium` e `utm_campaign`. No Google, isso acontece quando o parâmetro `_campanha` não foi criado.
- [ ] **5. Desligar o gclid no Google Ads.** A codificação automática deve ficar ativada; as UTMs vão no **Sufixo do URL final**, não substituem o gclid.
- [ ] **6. Montar link à mão.** Erros de digitação, `?` duplicado, espaço no nome. Gere sempre com `python3 ferramentas/utm.py gerar`, e na Meta use o texto dinâmico em vez de digitar em cada anúncio.

### Como auditar links que já existem

1. Monte uma planilha com **uma coluna chamada `url`** e um link por linha. Salve como CSV.
2. Rode:

```bash
python3 ferramentas/utm.py auditar caminho/do/arquivo.csv
```

3. A ferramenta lista cada link com problema e diz no fim quantos estão dentro do padrão.

Exemplo real, com o arquivo de teste `entregas/2026-11-06-guia-utm/exemplo-auditoria.csv`
(links errados de propósito, já com o site oficial):

```
linha 2: https://mayaprotege.com.br/?utm_source=Instagram&utm_medium=paid_social&utm_campaign=leads-plano-familiar-geral-202611
  - utm_source='Instagram' fora do padrão (minúsculas, sem acento, hífen)
  - utm_source 'Instagram' não está na convenção
linha 3: https://mayaprotege.com.br/?utm_source=ig&utm_medium=social&utm_campaign=leads-plano-familiar-geral-202611
  - utm_source 'ig' não está na convenção
  - utm_medium 'social' não está na convenção (o GA4 pode classificar como Unassigned)
linha 4: https://mayaprotege.com.br/?utm_source=email&utm_medium=email
  - falta utm_campaign
linha 5: https://mayaprotege.com.br/?UTM_SOURCE=email&utm_medium=email&utm_campaign=Promoção Novembro
  - parâmetro 'UTM_SOURCE' com maiúscula (o GA4 diferencia)
  - utm_campaign='Promoção Novembro' fora do padrão (minúsculas, sem acento, hífen)

1 de 5 links dentro do padrão.
```

### Auditoria dos links deste guia

Os 8 links finais da seção 4 foram salvos em `entregas/2026-11-06-guia-utm/links-finais.csv`
(coluna `url`) e auditados em 2026-11-06:

```
$ python3 ferramentas/utm.py auditar entregas/2026-11-06-guia-utm/links-finais.csv

8 de 8 links dentro do padrão.
```

Para corrigir, gere o link de novo com `gerar` e substitua o antigo onde ele estiver publicado.

---

## Antes de usar de verdade

- [x] Site oficial confirmado em `marca/marca.md` (mayaprotege.com.br) e links regenerados com ele.
- [x] Nomes de campanha com os planos reais (Serenidade, Familiar, Familiar Plus, Familiar Premium).
- [ ] Trocar o público de exemplo (`sp`, `geral`) pelo público ou região real de cada campanha.
- [ ] Conferir no site o caminho de qualquer página interna (ex.: página de um plano) antes de gerar link para ela.
- [ ] Decisão sobre incluir mediums próprios para WhatsApp e QR code na convenção (hoje: `referral` e `offline`).
- [ ] Caminhos de menu conferidos na interface atual da Meta e do Google (as plataformas mudam nomes de menus com frequência; os passos acima não foram conferidos na Central de Ajuda oficial nesta sessão).
