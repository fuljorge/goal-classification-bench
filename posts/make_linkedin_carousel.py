"""LinkedIn carousel (PT-BR), 7 slides, 1080x1350 pt (4:5).

    uv run --no-project --with reportlab python posts/make_linkedin_carousel.py \
        posts/linkedin-carousel.pt-BR.pdf docs/figures/figure1-accuracy-by-language.png

Uses the Segoe UI fonts shipped with Windows."""

import sys
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

OUT = Path(sys.argv[1])
FIG = Path(sys.argv[2])
W, H = 1080, 1350
M = 90  # side margin

pdfmetrics.registerFont(TTFont("UI", "C:/Windows/Fonts/segoeui.ttf"))
pdfmetrics.registerFont(TTFont("UIB", "C:/Windows/Fonts/segoeuib.ttf"))
pdfmetrics.registerFont(TTFont("UISB", "C:/Windows/Fonts/seguisb.ttf"))

INK = HexColor("#16181D")
MUTED = HexColor("#5C6370")
FAINT = HexColor("#E6E8EC")
ACCENT = HexColor("#1F6FD6")
ACCENT_BG = HexColor("#EAF2FD")
BG = HexColor("#FFFFFF")
TOTAL = 7


def wrap(text, font, size, width):
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if pdfmetrics.stringWidth(trial, font, size) <= width:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def para(c, text, x, y, font="UI", size=34, color=INK, width=W - 2 * M, leading=1.3):
    c.setFont(font, size)
    c.setFillColor(color)
    for line in wrap(text, font, size, width):
        c.drawString(x, y, line)
        y -= size * leading
    return y


def frame(c, n, kicker):
    c.setFillColor(BG)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    c.setFillColor(ACCENT)
    c.rect(0, H - 14, W, 14, stroke=0, fill=1)
    c.setFont("UISB", 26)
    c.setFillColor(ACCENT)
    c.drawString(M, H - 110, kicker.upper())
    c.setStrokeColor(FAINT)
    c.setLineWidth(2)
    c.line(M, 120, W - M, 120)
    c.setFont("UI", 24)
    c.setFillColor(MUTED)
    c.drawString(M, 78, "Fulvio Jorge da Silva  ·  goalbench  ·  doi:10.5281/zenodo.23233352")
    c.drawRightString(W - M, 78, f"{n}/{TOTAL}")


def big_number(c, x, y, value, label, sub, color=INK):
    c.setFont("UIB", 132)
    c.setFillColor(color)
    c.drawString(x, y, value)
    c.setFont("UISB", 34)
    c.setFillColor(INK)
    c.drawString(x, y - 56, label)
    c.setFont("UI", 28)
    c.setFillColor(MUTED)
    c.drawString(x, y - 98, sub)


c = canvas.Canvas(str(OUT), pagesize=(W, H))
c.setTitle("Seu classificador de intenções é 12 pontos pior em português")
c.setAuthor("Fulvio Jorge da Silva")

# 1 — hook
frame(c, 1, "Benchmark · IA em português")
y = para(
    c,
    "Seu classificador de intenções é 12 pontos pior em português.",
    M,
    H - 290,
    font="UIB",
    size=88,
    leading=1.12,
)
y = para(
    c,
    "Medi pequenos modelos de decisão e modelos de embeddings em mensagens de "
    "atendimento em PT-BR. Depois traduzi tudo para o inglês e rodei de novo, frase a frase.",
    M,
    y - 50,
    size=38,
    color=MUTED,
    leading=1.35,
)
c.setFont("UISB", 34)
c.setFillColor(ACCENT)
c.drawString(M, 200, "Arraste para ver o que muda  →")
c.showPage()

# 2 — setup
frame(c, 2, "Como medi")
y = para(
    c, "O mesmo pipeline de um agente em produção.", M, H - 230, font="UIB", size=62, leading=1.15
)
steps = [
    (
        "1",
        "Pré-seleção",
        "Um modelo de embeddings (Qwen3 0.6B ou 4B) escolhe os 10 objetivos mais parecidos com a mensagem.",
    ),
    (
        "2",
        "Decisão",
        "O modelo de decisão (Laya ou Strands Decider) dá uma probabilidade para cada uma das 10 opções.",
    ),
    (
        "3",
        "Combinação",
        "Os dois sinais são combinados e calibrados; o peso de cada um é ajustado nos exemplos.",
    ),
]
y -= 40
for num, title, text in steps:
    c.setFillColor(ACCENT_BG)
    c.roundRect(M, y - 150, W - 2 * M, 170, 18, stroke=0, fill=1)
    c.setFillColor(ACCENT)
    c.circle(M + 60, y - 50, 34, stroke=0, fill=1)
    c.setFont("UIB", 38)
    c.setFillColor(BG)
    c.drawCentredString(M + 60, y - 63, num)
    c.setFont("UIB", 36)
    c.setFillColor(INK)
    c.drawString(M + 120, y - 40, title)
    para(c, text, M + 120, y - 88, size=27, color=MUTED, width=W - 2 * M - 150, leading=1.3)
    y -= 200
y = para(
    c,
    "30 objetivos de atendimento · 10 exemplos cada · 150 frases de teste · "
    "3 sementes · 50 execuções. As mesmas frases traduzidas para o inglês.",
    M,
    y - 20,
    size=30,
    color=INK,
    leading=1.35,
)
c.showPage()

# 3 — headline numbers
frame(c, 3, "Resultado em PT-BR")
para(c, "Um bom embedding sozinho venceu tudo.", M, H - 230, font="UIB", size=62, leading=1.15)
big_number(
    c,
    M,
    860,
    "94,7%",
    "Embeddings sozinhos (Qwen3-4B)",
    "nenhum modelo de decisão melhorou isso",
    ACCENT,
)
big_number(c, M, 615, "85%", "Strands Decider (2B)", "o melhor modelo de decisão, sem ajuste")
big_number(
    c, M, 370, "52%", "Laya multilíngue", "abaixo dos embeddings que deveria complementar", MUTED
)
para(
    c,
    "Acerto top-1 em 150 frases, opções em ordem aleatória, média de 3 sementes. "
    "Decider × Laya: diferença significativa em todas as comparações (McNemar).",
    M,
    200,
    size=24,
    color=MUTED,
    leading=1.35,
)
c.showPage()

# 4 — position trap
frame(c, 4, "A armadilha")
y = para(
    c,
    "Em produção, a opção certa costuma vir primeiro.",
    M,
    H - 230,
    font="UIB",
    size=62,
    leading=1.15,
)
y = para(
    c,
    "As opções vão ordenadas por semelhança. Um modelo que só prefere a primeira "
    "opção parece ótimo sem ler a mensagem.",
    M,
    y - 30,
    size=34,
    color=MUTED,
    leading=1.35,
)
for base, value, label, color in [
    (
        720,
        "62%",
        "das vezes o Laya escolhe a 1ª opção quando ela vem por semelhança; com a ordem invertida, perde 11 pontos",
        MUTED,
    ),
    (
        475,
        "4 de 150",
        "frases mudam de resultado no Strands Decider quando a ordem é invertida: ele lê o conteúdo",
        ACCENT,
    ),
]:
    c.setFont("UIB", 96)
    c.setFillColor(color)
    c.drawString(M, base, value)
    para(c, label, M, base - 60, size=30, color=INK, leading=1.35)
c.setFillColor(ACCENT_BG)
c.roundRect(M, 170, W - 2 * M, 110, 18, stroke=0, fill=1)
c.setFont("UISB", 34)
c.setFillColor(ACCENT)
c.drawString(M + 40, 212, "Teste sempre com as opções embaralhadas.")
c.showPage()

# 5 — cost of language (figure)
frame(c, 5, "O custo do idioma")
y = para(
    c,
    "Nas mesmas frases, tudo acerta menos em português.",
    M,
    H - 230,
    font="UIB",
    size=62,
    leading=1.15,
)
fw = W - 2 * M
fh = fw * 702 / 1344
c.drawImage(str(FIG), M, y - 40 - fh, width=fw, height=fh)
y = y - 40 - fh - 70
y = para(
    c,
    "Pipeline completo com embeddings 0.6B: −8,4 pontos. Embeddings 0.6B: −12 pontos.",
    M,
    y,
    size=32,
    color=INK,
    leading=1.35,
)
para(
    c,
    "E o maior efeito do estudo: o checkpoint em inglês do Laya é 24 pontos melhor que o "
    "multilíngue. Para português, não existe checkpoint próprio.",
    M,
    y - 30,
    font="UISB",
    size=32,
    color=ACCENT,
    leading=1.35,
)
c.showPage()

# 6 — what to do
frame(c, 6, "O que fazer no seu agente")
y = para(
    c,
    "Cinco lições para classificar objetivos em PT-BR.",
    M,
    H - 230,
    font="UIB",
    size=62,
    leading=1.15,
)
y -= 30
for i, (title, text) in enumerate(
    [
        (
            "Invista primeiro no modelo de embeddings.",
            "Foi o melhor componente isolado nos dois idiomas.",
        ),
        (
            "Embaralhe as opções ao testar.",
            "A ordem de produção premia quem só gosta da primeira opção.",
        ),
        (
            "Ajuste a combinação com frases separadas.",
            "Os exemplos dos objetivos superestimam o modelo de decisão.",
        ),
        (
            "Avalie no idioma dos seus usuários.",
            "Em inglês, todos os componentes pareceram melhores.",
        ),
        (
            "Para português, planeje um fine-tuning.",
            "Um checkpoint por idioma valeu 24 pontos em inglês.",
        ),
    ],
    start=1,
):
    c.setFont("UIB", 44)
    c.setFillColor(ACCENT)
    c.drawString(M, y - 40, str(i))
    c.setFont("UISB", 34)
    c.setFillColor(INK)
    c.drawString(M + 70, y - 40, title)
    c.setFont("UI", 28)
    c.setFillColor(MUTED)
    c.drawString(M + 70, y - 84, text)
    y -= 165
c.showPage()

# 7 — reproduce
frame(c, 7, "Reproduza você mesmo")
y = para(
    c,
    "Tudo aberto: código, dados e os registros das 50 execuções.",
    M,
    H - 230,
    font="UIB",
    size=62,
    leading=1.15,
)
y = para(
    c,
    "Recalcule todos os números em cerca de um minuto, sem GPU e sem servidor de modelo.",
    M,
    y - 30,
    size=34,
    color=MUTED,
    leading=1.35,
)
y -= 70
for label, value in [
    ("Repositório", "github.com/fuljorge/goal-classification-bench"),
    ("DOI (Zenodo)", "10.5281/zenodo.23233352"),
    ("Post completo", "link nos comentários"),
]:
    c.setFont("UISB", 28)
    c.setFillColor(MUTED)
    c.drawString(M, y, label.upper())
    c.setFont("UIB", 38)
    c.setFillColor(INK)
    c.drawString(M, y - 52, value)
    y -= 150
c.setFillColor(ACCENT_BG)
c.roundRect(M, 170, W - 2 * M, 130, 18, stroke=0, fill=1)
para(
    c,
    "Próximo experimento: fine-tuning em PT-BR. Será que fecha a diferença?",
    M + 40,
    250,
    font="UISB",
    size=32,
    color=ACCENT,
    width=W - 2 * M - 80,
    leading=1.3,
)
c.showPage()
c.save()
print("ok", OUT)
