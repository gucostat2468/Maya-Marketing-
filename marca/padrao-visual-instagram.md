# Padrão visual do Instagram: Maya Protege

**Versão 1.2 · 12/11/2026 · Dono: Diretor de Arte.** (1.1: seção 13, botões e chamadas para ação por formato. 1.2: seção 14, sistema gráfico e identidade por série; logo oficial no lugar do espaço "LOGO"; regra de fotografia atualizada.) Regra para toda a equipe (Diretor de Arte,
Social Media, Copywriter, Gestor de Meta Ads, Guardião da Marca). Vale para feed, carrossel e
stories, orgânico e anúncio. Base: `marca/marca.md` e a auditoria
`entregas/2026-11-06-padrao-visual/auditoria-feed.md`. Exemplos aplicados:
`entregas/2026-11-06-padrao-visual/pecas/`.

> Em uma frase: **uma ideia, poucas palavras, texto grande, uma palavra em itálico verde,
> muito respiro.** Se a peça precisa de explicação, a explicação vai na legenda.

---

## 1. Tokens (copiar no topo de todo HTML)

```css
:root {
  /* Cores da marca (amostradas do site; confirmar com o manual) */
  --verde-profundo: #091D19;   /* fundo escuro */
  --verde-profundo-2: #0A1B14; /* variação de fundo / gradiente */
  --verde-botao: #0C332A;      /* CTA em fundo claro, selos */
  --verde-emblema: #43CB6D;    /* destaque em fundo ESCURO */
  --verde-acao: #0D9448;       /* CTA em fundo escuro, destaque em fundo CLARO */
  --menta: #EFFAF5;            /* cartões */
  --fundo-claro: #F8FAF9;      /* fundo claro */
  --branco: #FFFFFF;
  /* Derivadas (texto e linhas) */
  --texto-apoio-escuro: #C5D3CE; /* corpo sobre fundo escuro */
  --texto-apoio-claro: #3E524C;  /* corpo sobre fundo claro */
  --linha-claro: #D7E6DF;
  --linha-escuro: rgba(255,255,255,0.14);
  /* Fontes SUBSTITUTAS (ver seção 3) */
  --serifa: "Libre Baskerville", Georgia, serif;
  --sans: "Inter", "Helvetica Neue", Arial, sans-serif;
  --manuscrita: "Caveat", cursive;
  --margem: 80px;
}
```

**Dourado/amarelo não é cor da marca.** Exceção única: símbolo de campanha pública (ex.: laço do
Setembro Amarelo), só no símbolo e na palavra que nomeia a campanha.

## 2. Grade e margens

### Feed 1080 x 1350 (4:5) e carrossel
- **Margem fixa de 80 px nos 4 lados.** Área útil: 920 x 1190 px. Nada (texto, logo, CTA,
  contador) fora dela. Só fundos, formas decorativas e fotos podem sangrar.
  Motivo: a grade do perfil recorta o 4:5 em 3:4 e corta ~34 px de cada lateral; 80 px dá folga.
- **6 colunas** de 140 px com calha de 16 px (6 x 140 + 5 x 16 = 920).
- **Ritmo vertical de 8 px:** todo espaçamento é múltiplo de 8 (8, 16, 24, 32, 48, 64, 96).
- **Zonas fixas:**

| Zona | Posição (px) | O que vai |
|---|---|---|
| Topo | y 80 a 136 | Logo à esquerda (x 80); contador de slide à direita (alinhado em x 1000) |
| Conteúdo | y 200 a 1110 | Título, apoio, gráfico ou foto |
| Rodapé | y 1174 a 1270 | 1 chamada em formato de instrução (ícone + texto) à esquerda (x 80), ou nada. Ver seção 13 |

- Alinhamento **à esquerda** por padrão. Centralizado só em peça de símbolo único (data,
  campanha) e nunca misturado com bloco alinhado à esquerda na mesma peça.

### Stories e Reels 1080 x 1920 (9:16)
- **Áreas cobertas pela interface:** nada importante nos **250 px de cima** (y 0 a 250) nem nos
  **340 px de baixo** (y 1580 a 1920). Laterais: 80 px.
- Área segura: x 80 a 1000, y 250 a 1580 (920 x 1330 px).
- Logo em x 80, y 280. **Zona da figurinha de link** (seção 13) com a base em **no máximo y 1540**.

## 3. Tipografia

As **fontes oficiais não foram confirmadas** (marca.md, seção 9). Até o manual chegar, usar estas
**substitutas do Google Fonts**, escolhidas por se parecerem com o site:

| Papel | Substituta | Pesos | Por que |
|---|---|---|---|
| Títulos | **Libre Baskerville** | Regular 400 e Itálico 400 | Serifa clássica de contraste médio, itálico elegante parecido com "*proteger*" do site |
| Corpo, CTA, rótulos | **Inter** | 400, 500, 600 | O corpo do site é uma sans geométrica-humanista muito próxima da Inter |
| Nota manuscrita (rara) | **Caveat** | 600 | Parecida com as notas do feed atual |

Link: `https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital,wght@0,400;1,400&family=Inter:wght@400;500;600&family=Caveat:wght@600&display=swap`

**Títulos em serifa REGULAR, nunca negrito.** O peso vem do tamanho, não da espessura.

### Escala (px na peça)

| Estilo | Feed / carrossel | Stories | Fonte | Entrelinha |
|---|---|---|---|---|
| Display (frase curta, até 7 palavras) | 104 | 120 | Serifa 400 | 1,08 |
| Título | 84 a 92 | 104 | Serifa 400 | 1,12 |
| Título de slide interno | 68 a 76 | 84 | Serifa 400 | 1,15 |
| Subtítulo / apoio | 40 a 46 | 48 a 52 | Inter 400 | 1,35 |
| **Corpo (mínimo)** | **38 (nunca abaixo de 34)** | **44 (nunca abaixo de 42)** | Inter 400/500 | 1,4 |
| CTA | 36, Inter 600 | 42, Inter 600 | Inter 600 | 1 |
| Rótulo (sobretítulo, contador) | 28, caixa alta, espaçamento 0,14 em | 32 | Inter 600 | 1 |
| Nota legal ("conforme o plano") | 28 (mínimo 26) | 30 | Inter 400 | 1,35 |

- Rótulo e nota legal são os **únicos** textos abaixo do corpo mínimo, e nunca carregam a mensagem.
- Máximo de **2 famílias por peça** (serifa + Inter). A manuscrita entra como terceira só em nota
  de até 6 palavras e em no máximo **1 a cada 4 posts**.
- Título com no máximo **5 linhas** no feed e **4 linhas** na capa.

### Regra do itálico verde
- **No máximo 1 destaque por peça**, de 1 a 3 palavras, em **itálico** da serifa (nunca negrito,
  nunca caixa alta, nunca linha inteira).
- Cor: `--verde-emblema` (#43CB6D) sobre fundo escuro; `--verde-acao` (#0D9448) sobre fundo claro
  (#43CB6D no claro não tem contraste).
- O destaque é **a palavra que carrega a ideia** ("*organizado*", "*difíceis demais*", "*ato de amor*").

## 4. Quantidade de texto e de elementos

| Peça | Palavras na imagem (máx.) | Título (máx.) |
|---|---|---|
| Post único de feed | 25 | 12 |
| Capa de carrossel | 12 | 12 |
| Slide interno | 30 | 6 |
| Slide final | 20 | 10 |
| Tela de stories | 25 | 8 |

- A contagem **não inclui** rótulo (sobretítulo), contador de slide, nota legal e o espaço do logo.
- **1 ideia por peça / por slide.** Se precisa de "e também", é outro slide.
- **1 CTA por peça.** Em carrossel, o CTA fica no slide final; a capa pode ter só o indicador
  "Deslize" (navegação, não CTA).
- **Até 5 elementos por peça:** logo, título, apoio, 1 gráfico ou foto, CTA. Contador de slide e
  nota legal não contam.
- Nada de selo + manuscrita + ícones + CTA juntos. Escolha um apoio visual.
- Textos sem verbo de medo ou urgência (marca.md, seção 8).

## 5. Cores por fundo

| | Fundo escuro | Fundo claro |
|---|---|---|
| Fundo | #091D19 (pode ter luz radial #0F2B24) | #F8FAF9 |
| Título | #FFFFFF | #091D19 |
| Destaque itálico | #43CB6D | #0D9448 |
| Corpo | #C5D3CE | #3E524C |
| Cartão | rgba(255,255,255,0.06) com borda #FFFFFF 14% | #EFFAF5 ou #FFFFFF com borda #D7E6DF |
| Chamada (instrução) | ícone #43CB6D + texto branco | ícone #0D9448 + texto #091D19 |

Proporção aproximada **70 / 25 / 5**: fundo / texto e cartões / verde de destaque. O verde
vivo é tempero, não fundo.

## 6. Fotografia

- **Só foto real:** licenciada (banco de imagens pago, como o Adobe Stock, com a licença guardada)
  ou própria, com autorização de imagem por escrito. **Nunca foto, pessoa ou cena gerada por IA.**
- **Modelos de banco não são clientes:** nunca usar como depoimento, nem com nome, idade, cidade
  ou fala atribuída. Sem marca d'água. Guardar o ID da foto no nome do arquivo.
- **Onde faz sentido:** peças de afeto (datas, capa de carrossel). Conteúdo de lista, checklist e
  comparativo continua gráfico. Toda peça com foto tem uma **alternativa gráfica** pronta.
- **Layout aprovado (12/11/2026):** foto no topo (até 880 px de altura no feed), **degradê para o
  verde profundo** na base (0% → 84% → #091D19), véu verde `#0C332A` em luz suave (35% a 45%),
  saturação entre 78% e 92%; logo selo sobre a foto, fora de rostos; rótulo, título serifado e
  chamada sobre o verde profundo. **Texto e logo nunca sobre rosto.**
  Exemplo: `entregas/2026-11-12-pecas-com-foto/feed-dia-da-familia-foto.html`.
- **Não usar:** tristeza, choro, caixão, hospital em destaque; foto com logo gerado ou deformado;
  prints recortados. Atenção redobrada a foto de pessoa idosa ao lado de texto de plano: passa
  pelo Guardião.
- **Frequência:** no máximo **1 post com foto a cada 3** na grade; nunca 2 fotos de família seguidas.

## 7. Ícones e formas

- **Ícones de linha** (traço de 3 px na peça, cantos arredondados), 48 a 56 px, dentro de quadrado
  de 96 a 104 px com raio 24 (menta no claro; #0C332A ou menta no escuro).
- **Só em listas**, 1 por item, **no máximo 4 por peça**. Nunca como decoração solta. Nunca emoji.
- O ícone de WhatsApp só aparece em CTA que **abre o WhatsApp**.
- **Formas:** a fita hexagonal de 6 facetas (seção 14). **1 grafismo por peça.** O hexágono solto em
  contorno, usado até a versão 1.1, sai de uso. Nunca desenhar ou imitar o logotipo.
- Cartões com raio 32 a 40 px. **Pílula cheia com cara de botão não é usada em peça do Instagram** (seção 13).

## 8. Logo

- **Arquivo oficial:** `marca/logo/maya-protege-selo.png` (selo circular). Usar **como está**: sem
  redesenhar, recolorir, distorcer ou recortar. O espaço tracejado "LOGO" não é mais usado.
- **Posição fixa:** canto superior esquerdo, x 80, y 80. **Tamanho: 120 a 160 px no feed (padrão
  136); 148 px no stories** (x 80, y 280). Máximo 200 px (o arquivo tem 538 px).
- Em fundo escuro, um fio de 2 px branco a 10% e sombra suave soltam o selo do fundo; em fundo
  claro, só a sombra. Isso é apoio do layout, não alteração do logo.
- Aparece **1 vez por peça**. Carrossel: na capa e no slide final; slides internos levam o rótulo
  da série e o contador.
- Sobre foto, o selo fica fora de rostos. Para impresso e peças grandes falta o SVG original.

## 9. Carrossel

| Slide | Regra |
|---|---|
| **Capa** | Rótulo do tema (opcional) + título de até 12 palavras + 1 gráfico. Logo no topo, contador "1/N" à direita, "Deslize" + seta no rodapé. Não entregar o conteúdo na capa. |
| **Internos** | Número do item (quadrado #0C332A com número em serifa branca, 88 px), título de até 6 palavras, até 4 itens de lista ou 1 frase. Mesmo fundo e mesma posição de título em todos. |
| **Final** | Fecho em 1 frase (com o itálico verde) + 1 CTA. Logo no topo. |

- Mesma grade em todos os slides: o título começa sempre em y 280 nos internos.
- Fundo dos internos sempre o mesmo; o final pode inverter (escuro) para marcar o fecho.

## 10. Grade do perfil harmoniosa

- **Alternar estritamente** fundo escuro e fundo claro na ordem de publicação (E, C, E, C...).
  Numa grade de 3 colunas isso forma um **xadrez** automático. Carrossel conta pela capa.
- No máximo **1 post com foto a cada 3**; os outros dois tipográficos/gráficos.
- O texto do título sempre na mesma região (terço superior, alinhado à esquerda): de longe, a
  grade ganha uma "linha de leitura" comum.
- Posts fixados (até 3): capa institucional, "O que está incluído", e o melhor conteúdo
  educativo; os três seguindo a alternância.
- Nunca publicar montagem de vários slides numa miniatura.

## 11. Checklist antes de entregar (o Diretor de Arte assina; o Guardião confere)

1. [ ] A mensagem é entendida em **2 segundos** (teste: cobrir tudo menos o título).
2. [ ] **Um único foco visual.**
3. [ ] Palavras dentro do limite da seção 4 (contadas).
4. [ ] Corpo **≥ 34 px** no feed / **≥ 42 px** no stories; título ≥ 68 px.
5. [ ] Contraste: corpo ≥ 4,5:1, título e CTA ≥ 3:1.
6. [ ] Margem de 80 px respeitada; nada cortado (a ferramenta de renderização não avisou corte).
7. [ ] Stories: nada importante em y < 250 ou y > 1580.
8. [ ] **1 CTA**, visível, com verbo da marca, **no formato certo para o lugar** (seção 13): stories com zona da figurinha limpa; anúncio sem botão desenhado; feed orgânico como instrução, sem pílula.
9. [ ] **1 destaque** em itálico verde, no máximo.
10. [ ] Logo oficial (selo) na posição fixa, 1 vez, entre 120 e 160 px no feed.
11. [ ] Foto: real, licenciada ou própria, **nunca de IA**; modelo de banco não é depoimento; nada sobre rosto (ou nenhuma foto).
12. [ ] Ícones ≤ 4, só em lista, sem emoji.
13. [ ] Itens de plano citados existem em marca.md, seção 2; sem preço, "seguro" ou número não
    confirmado.
14. [ ] Cabe na alternância da grade (o post anterior era escuro ou claro?).
15. [ ] PNG aberto e conferido no tamanho de celular (reduzir para 375 px de largura e ler).

## 12. Especificações para o Figma

Cada peça entregue vem com camadas em `especificacoes-figma.json` (posição absoluta, tamanho,
cor, raio, fonte, tamanho, peso, estilo, alinhamento, entrelinha). No Figma: frame do tamanho do
formato, grade de layout de 6 colunas com margem 80 e calha 16, estilos de texto com os nomes da
seção 3 e estilos de cor com os nomes dos tokens da seção 1.

## 13. Botões e chamadas para ação por formato

**No Instagram, nada desenhado dentro da imagem é clicável.** Um botão desenhado que parece
clicável e não é frustra quem toca e passa a impressão de peça quebrada. Por isso a chamada
muda conforme o lugar onde a peça aparece:

| Formato | O que é clicável de verdade | O que a arte faz |
|---|---|---|
| **Stories** | A **figurinha de link** do Instagram, colada sobre a arte na hora de publicar | Reserva a **zona da figurinha** limpa e dá uma pista leve |
| **Anúncio (Meta Ads)** | O **botão nativo** do anúncio ("Enviar mensagem" para WhatsApp, "Saiba mais" para o site), que fica **fora da imagem** | **Não desenha botão nem chamada**; a arte termina na mensagem |
| **Feed orgânico e carrossel** | Nada na imagem. Só o link da bio e as ações nativas (curtir, comentar, salvar, compartilhar) | Chamada em formato de **instrução** (ícone + texto), **sem pílula** |

### 13.1 Stories: zona da figurinha
- **Zona da figurinha:** 720 x 150 px, **centralizada** (x 180 a 900), dentro da área segura,
  com a base **acima de y 1580** (padrão: y 1388 a 1538). Variáveis CSS: `--zona-x`, `--zona-y`,
  `--zona-l`, `--zona-a`; marcar o elemento com `data-slot="figurinha-link"`.
- **Nada desenhado por baixo da zona:** sem pílula, sem cartão, sem texto. Só o fundo.
- **Pista visual leve** logo acima da zona: 1 frase de até 8 palavras em Inter 600, 42 px, com
  uma seta para baixo em #43CB6D (ex.: "Toque no link e fale com a gente"). A pista é
  centralizada por estar presa à figurinha; é a única exceção à regra de alinhamento à esquerda.
- Toda peça de stories com link é entregue em **duas versões**: a arte para publicar (zona
  limpa) e um **guia** (`-guia.png`) com a zona tracejada e o aviso "Cole aqui a figurinha de
  link · GUIA · NÃO PUBLICAR", só para quem vai publicar.
- O texto da figurinha é personalizado no app (ex.: "Fale com a gente"); ver o kit de publicação
  da entrega.

### 13.2 Anúncio: o botão é nativo
- A versão de anúncio **não tem CTA desenhado**. O rodapé fica vazio (só fundo e forma).
- A chamada vai no botão nativo escolhido no Gerenciador de Anúncios e no texto principal.
- Nome do arquivo com sufixo `-anuncio`. Nunca reaproveitar a versão de feed orgânico com
  "link na bio" em anúncio (em anúncio não há bio para onde ir).

### 13.3 Feed orgânico e carrossel: chamada como instrução
- **Ícone de linha + texto**, sem fundo, sem pílula, sem borda, na zona do rodapé (x 80, y 1174
  a 1270). Inter 600, 36 px. Ícone 44 px em #43CB6D (fundo escuro) ou #0D9448 (fundo claro).
- Pode destacar em verde **só o trecho da ação** ("link na bio", "A, B ou C"), na mesma Inter
  (não conta como o itálico verde da serifa).
- **Só ações que existem de verdade:**

| Ação | Texto modelo | Ícone |
|---|---|---|
| Salvar | "Salve este post" | marcador (bookmark) |
| Comentar | "Responda nos comentários: A, B ou C" | balão de conversa |
| Compartilhar | "Compartilhe com quem precisa saber" | avião de papel |
| Link na bio | "Conheça os planos: link na bio" | elo de corrente |
| WhatsApp | "Chame no WhatsApp: (11) 94552-4233" | balão de conversa (o ícone do WhatsApp fica para o que abre o WhatsApp de verdade: figurinha e anúncio, seção 7) |

- Nunca escrever "Clique aqui" ou "Toque aqui" numa peça de feed: não há onde tocar.

## 14. Sistema gráfico e identidade por série

Exemplos aplicados: `entregas/2026-11-10-pecas-dezembro/pecas/` (o código que desenha as formas
está em `gerar_pecas.py`, funções `anel` e `fita`).

### 14.1 O grafismo: fita hexagonal de 6 facetas
- Vem das formas verdes de vidro do site, **não do emblema**. É uma família de formas, e nunca
  uma cópia do logo: **proibido anel de 8 pétalas** e proibido grafismo pequeno e inteiro perto do selo.
- **Dois estados:** *anel frontal* (6 trapézios separados por um vão de 7 a 11 px, cada um com
  chanfro claro por fora e escuro por dentro) e *fita em perspectiva* (parede hexagonal vista de
  cima, face de dentro mais escura, fio de luz na borda de cima).
- **Faceta acesa ou apagada:** acesa é vidro verde (#2DBB66 a #9DF2BB no escuro; #0D9448 a #49CF72
  no claro); apagada é só contorno (verde a 42%) com preenchimento a 7%. Quando o anel conta
  alguma coisa (itens, etapas), **cada faceta acesa é um item**.
- **Escala e posição:** sempre grande (raio de 260 a 560 px no feed) e **cortado por pelo menos
  uma borda**. Nunca atrás de texto: 40 px de folga, no mínimo, do título e da chamada.
- **Profundidade:** brilho desfocado atrás das facetas acesas (até 50%), luz radial no fundo e
  grão fino (16% no escuro, 5% no claro). Sem sombra dura, sem neon.
- **Faixa:** o trapézio pequeno (34 x 14 px, inclinado 30°) marca o rótulo da série; a tira de
  trapézios é o contador de slides.

### 14.2 Números e listas como imagem
- Número que carrega informação ("24h", "100 km") vai em **serifa regular de 200 a 232 px**, unidade
  em 96 px, branco com degradê leve para menta. Máximo de 2 por slide.
- Número de ordem pode aparecer gigante ao fundo (700 px, #E7F6EE no claro), sem competir com o texto.
- Listas: linhas com fio de 2 px entre os itens, marcador hexagonal com "check" de 92 px, texto
  Inter 500 de 46 px. Sem pictograma de urna, caixão ou pessoa.

### 14.3 Identidade por série

| Série | Fundo | Grafismo | Rótulo |
|---|---|---|---|
| O que está incluído | Escuro (#091D19 com luz no canto superior direito) | Anel frontal que acende por item; números gigantes | O QUE ESTÁ INCLUÍDO |
| Mito ou verdade | Claro (#F8FAF9) | Anel partido em duas metades, verde escuro e verde vivo | MITO OU VERDADE? |
| Datas | Escuro com "aurora" verde na base, ou foto real (seção 6) | Fitas em perspectiva de tamanhos diferentes | DIA + NOME DA DATA |
| Organização familiar | Menta (#F1FBF6 a #DCF2E6) | Fichário: divisórias brancas com aba numerada | ORGANIZAÇÃO FAMILIAR |
| Séries novas | Escolher fundo e estado do grafismo ainda não usados em sequência | | |

- A série mantém fundo, grafismo e posição do título em todos os posts; o que muda é o conteúdo.
- Uma série pode fixar a própria altura de título nos slides internos (o fichário usa y 424),
  desde que seja igual em todos os slides.
- A alternância escuro/claro da seção 10 continua valendo: ao montar o calendário, alternar as séries.
- **Teste da grade:** antes de entregar, montar `grade-simulada.png` (recorte central 3:4) com as
  últimas 6 peças. Se duas vizinhas parecerem a mesma peça, refazer.
