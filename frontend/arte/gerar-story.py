# -*- coding: utf-8 -*-
"""
Gera o video do convite para story (1080x1920, vertical), para postar no
Instagram/WhatsApp: a bonequinha sem fundo sobre o rosa do convite, com a
legenda gravada na imagem, o audio e o endereco em destaque.

    python arte/gerar-story.py            (rodar de dentro de frontend/)
    python arte/gerar-story.py --previa   (so um quadro em PNG, para conferir)

Sai em ../story-gc-styllus.mp4 (raiz do projeto, fora do site).

Reaproveita o recorte de arte/gerar-video.py, mas na resolucao do recorte
original (960x720) em vez da do site (720x540): no story ela fica com 1080 de
largura, e aumentar a do site deixaria a imagem borrada. O audio sai do video
do site (public/assets/bonequinha.mp4), que ja tem as partes juntas: rode o
gerar-video.py antes, se alguma parte mudou.

Textos (legendas, endereco, data) vem de src/configuracaoTema.js: mudou la,
e so rodar de novo.

Precisa das fontes do convite, baixadas sozinhas na primeira vez para
~/.cache/convite-gc-styllus/fontes/ (Google Fonts, licenca OFL).
"""
import datetime
import importlib.util
import itertools
import os
import re
import subprocess
import sys
import urllib.request

import numpy as np
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("gerador", os.path.join(AQUI, "gerar-video.py"))
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)

FRONTEND = g.FRONTEND
TEMA = os.path.join(FRONTEND, "src", "configuracaoTema.js")
PARTES_JS = g.PARTES_JS
AUDIO_DE = g.DESTINO
SAIDA = os.path.join(g.PASTA_PARTES, "story-gc-styllus.mp4")
PREVIA = os.path.join(g.PASTA_PARTES, "story-previa.png")

W, H = 1080, 1920
FPS = g.FPS
CRF = 20

# O recorte na resolucao do corte 4:3 original, sem reduzir
g.LARGURA, g.ALTURA = 960, 720
# Faixa da bonequinha: 4:3 na largura toda
FAIXA_Y, FAIXA_H = 600, 810

# Cores do convite (src/index.css)
ROSA = (209, 18, 111)
ROSA_ESCURO = (163, 13, 87)
ROSA_CLARO = (253, 228, 239)
FUNDO_ESCURO = (249, 211, 228)
VINHO = (94, 18, 57)
DOURADO = (201, 162, 77)
DOURADO_CLARO = (240, 220, 166)
BRANCO = (255, 255, 255)

PASTA_FONTES = os.path.join(os.path.expanduser("~"), ".cache", "convite-gc-styllus", "fontes")
FONTES_URL = "https://raw.githubusercontent.com/google/fonts/main/ofl/"
FONTES = {
    "playfair": "playfairdisplay/PlayfairDisplay%5Bwght%5D.ttf",
    "parisienne": "parisienne/Parisienne-Regular.ttf",
    "quicksand": "quicksand/Quicksand%5Bwght%5D.ttf",
}
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
         "agosto", "setembro", "outubro", "novembro", "dezembro"]
SEMANA = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]


def fonte(nome, tamanho, peso=None):
    arq = os.path.join(PASTA_FONTES, FONTES[nome].split("/")[-1].replace("%5B", "[").replace("%5D", "]"))
    if not os.path.exists(arq):
        os.makedirs(PASTA_FONTES, exist_ok=True)
        print(f"baixando a fonte {nome}...")
        urllib.request.urlretrieve(FONTES_URL + FONTES[nome], arq + ".parcial")
        os.replace(arq + ".parcial", arq)
    f = ImageFont.truetype(arq, tamanho)
    if peso:
        f.set_variation_by_axes([peso])
    return f


def tempo_no_video():
    """Mesma conta de src/legendas.js, com os dados de src/partesVideo.js."""
    texto = open(PARTES_JS, encoding="utf-8").read()
    bloco = lambda nome: texto[texto.index(nome):].split("}")[0]
    inicios = {k: float(v) for k, v in re.findall(r'"(\w+)":\s*([\d.]+)', bloco("INICIO_PARTES"))}
    trechos = {}
    numero = r"([\d.]+),\s*"
    for k, lista in re.findall(r'"(\w+)":\s*\[(.*)\],', bloco("TRECHOS")):
        trechos[k] = [tuple(map(float, q)) for q in re.findall(r"\[" + numero * 3 + r"([\d.]+)\]", lista)]

    def conta(parte, t):
        desloc = 0.0
        for oi, of, ni, nf in trechos.get(parte, []):
            if t >= of:
                desloc = nf - of
            elif t > oi:
                return inicios[parte] + ni + (t - oi) * (nf - ni) / (of - oi)
            else:
                break
        return inicios[parte] + t + desloc
    return inicios, conta


def ler_tema():
    texto = open(TEMA, encoding="utf-8").read()
    inicios, conta = tempo_no_video()
    legendas = []
    for linha in texto.splitlines():
        if linha.strip().startswith("//"):
            continue
        achou = re.search(r"\{\s*parte:\s*'(\w+)',\s*inicio:\s*([\d.]+),\s*fim:\s*([\d.]+),\s*texto:\s*'([^']*)'", linha)
        if achou and achou.group(1) in inicios:
            parte = achou.group(1)
            legendas.append((conta(parte, float(achou.group(2))), conta(parte, float(achou.group(3))), achou.group(4)))
    rua = re.search(r"\brua:\s*'([^']*)'", texto).group(1)
    bairro = re.search(r"\bbairro:\s*'([^']*)'", texto).group(1)
    hora, data = re.search(r"dataInicio:\s*'([^']*)'", texto).group(1).split(" ")
    dia, mes, ano = map(int, data.split("/"))
    h, m = hora.split(":")
    quando = f"{SEMANA[datetime.date(ano, mes, dia).weekday()]}, {dia} de {MESES[mes - 1]} · a partir das {int(h)}h{m if m != '00' else ''}"
    return legendas, rua, bairro, quando


def degrade(h, cores):
    """Degrade vertical entre (posicao 0-1, cor) -> array h x 3."""
    pos = np.linspace(0, 1, h)
    return np.stack([np.interp(pos, [p for p, _ in cores], [c[i] for _, c in cores]) for i in range(3)], axis=1)


def centro(d, y, texto, f, cor):
    x0, _, x1, _ = d.textbbox((0, 0), texto, font=f)
    d.text(((W - (x1 - x0)) / 2 - x0, y), texto, font=f, fill=cor)


def fundo_fixo(rua, bairro, quando):
    """Tudo que nao muda: degrade, cabecalho, faixa da bonequinha e endereco."""
    fundo = degrade(H, [(0, BRANCO), (0.55, (255, 243, 248)), (1, ROSA_CLARO)])
    img = np.repeat(fundo[:, None, :], W, axis=1)
    img[FAIXA_Y:FAIXA_Y + FAIXA_H] = degrade(FAIXA_H, [(0, ROSA_CLARO), (1, FUNDO_ESCURO)])[:, None, :]
    base = Image.fromarray(img.astype(np.uint8))
    d = ImageDraw.Draw(base)

    # cabecalho, abaixo da barra de cima do story (~200px)
    centro(d, 205, "GC STYLLUS", fonte("playfair", 118, 800), ROSA)
    d.line([(250, 360), (505, 360)], fill=DOURADO, width=4)
    d.line([(575, 360), (830, 360)], fill=DOURADO, width=4)
    d.polygon([(540, 344), (556, 360), (540, 376), (524, 360)], fill=DOURADO)
    centro(d, 365, "Inauguração", fonte("parisienne", 104), ROSA)
    centro(d, 520, quando, fonte("quicksand", 40, 700), VINHO)

    # faixa da bonequinha com a linha dourada embaixo, como no convite
    d.rectangle([0, FAIXA_Y + FAIXA_H, W, FAIXA_Y + FAIXA_H + 5], fill=DOURADO)

    # endereco em destaque, acima da barra de resposta do story (~250px)
    y0, y1 = 1455, 1700
    d.rounded_rectangle([60, y0 + 10, W - 60, y1 + 10], radius=40, fill=(240, 205, 222))
    d.rounded_rectangle([60, y0, W - 60, y1], radius=40, fill=BRANCO, outline=DOURADO, width=5)
    f_rot = fonte("quicksand", 34, 700)
    rotulo = "ONDE VAI SER"
    x0, _, x1, _ = d.textbbox((0, 0), rotulo, font=f_rot)
    larg = (x1 - x0) + 44
    xi = (W - larg) / 2
    # alfinete do mapa
    d.ellipse([xi, y0 + 34, xi + 30, y0 + 64], fill=ROSA)
    d.polygon([(xi + 3, y0 + 55), (xi + 27, y0 + 55), (xi + 15, y0 + 80)], fill=ROSA)
    d.ellipse([xi + 9, y0 + 43, xi + 21, y0 + 55], fill=BRANCO)
    d.text((xi + 44 - x0, y0 + 30), rotulo, font=f_rot, fill=ROSA)
    centro(d, y0 + 84, rua, fonte("playfair", 62, 700), VINHO)
    centro(d, y0 + 166, bairro, fonte("quicksand", 46, 700), ROSA_ESCURO)
    return np.asarray(base, np.float32)


def imagem_legenda(texto):
    """Caixa vinho com a frase, como a .legenda do convite. Devolve RGBA."""
    f = fonte("quicksand", 48, 700)
    linhas, atual = [], ""
    for palavra in texto.split():
        teste = (atual + " " + palavra).strip()
        if f.getlength(teste) > 900 and atual:
            linhas.append(atual)
            atual = palavra
        else:
            atual = teste
    linhas.append(atual)
    alt_linha = 62
    larg = int(max(f.getlength(l) for l in linhas)) + 64
    alt = alt_linha * len(linhas) + 34
    img = Image.new("RGBA", (larg, alt), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, larg - 1, alt - 1], radius=26, fill=(*VINHO, 214))
    for i, l in enumerate(linhas):
        d.text(((larg - f.getlength(l)) / 2, 14 + i * alt_linha), l, font=f, fill=BRANCO)
    return np.asarray(img, np.float32)


def colar(quadro, rgba, x, y):
    h, w = rgba.shape[:2]
    a = rgba[..., 3:] / 255
    area = quadro[y:y + h, x:x + w]
    area[:] = rgba[..., :3] * a + area * (1 - a)


def montar(base, cor, alfa, legenda):
    quadro = base.copy()
    pessoa = np.asarray(Image.fromarray(cor).resize((W, FAIXA_H), Image.LANCZOS), np.float32)
    a = np.asarray(Image.fromarray(alfa).resize((W, FAIXA_H), Image.LANCZOS), np.float32)[..., None] / 255
    faixa = quadro[FAIXA_Y:FAIXA_Y + FAIXA_H]
    faixa[:] = pessoa * a + faixa * (1 - a)
    if legenda is not None:
        h, w = legenda.shape[:2]
        colar(quadro, legenda, (W - w) // 2, FAIXA_Y + FAIXA_H - h - 22)
    return quadro.astype(np.uint8)


def gerar(previa):
    legendas, rua, bairro, quando = ler_tema()
    base = fundo_fixo(rua, bairro, quando)
    caixas = [(ini, fim, imagem_legenda(t)) for ini, fim, t in legendas]

    def legenda_em(t):
        for ini, fim, img in caixas:
            if ini <= t < fim:
                return img
        return None

    partes = g.listar_partes()
    sessao = g.obter_modelo()

    if previa:
        quadros = itertools.islice(g.quadros_da_parte(partes[0]), 80)
        for j, (cor, alfa) in enumerate(g.recortar_parte(sessao, quadros)):
            if j == 72:
                Image.fromarray(montar(base, cor, alfa, legenda_em(j / FPS))).save(PREVIA)
                print("previa:", PREVIA)
                return

    proc = subprocess.Popen(
        [g.ffmpeg(), "-v", "error", "-y",
         "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
         "-i", AUDIO_DE, "-map", "0:v", "-map", "1:a",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", str(CRF), "-preset", "medium",
         "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", SAIDA],
        stdin=subprocess.PIPE,
    )
    i = 0
    for parte in partes:
        print(f"recortando {os.path.basename(parte)}...", flush=True)
        quadros = g.quadros_da_parte(parte)
        for cor, alfa in g.recortar_parte(sessao, quadros):
            proc.stdin.write(montar(base, cor, alfa, legenda_em(i / FPS)).tobytes())
            i += 1
    proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit("o ffmpeg falhou ao gerar o story")
    print(f"\n{i} quadros ({i / FPS:.2f}s) -> {SAIDA}: {os.path.getsize(SAIDA) / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    gerar("--previa" in sys.argv)
