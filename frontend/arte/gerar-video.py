# -*- coding: utf-8 -*-
"""
Gera o video da bonequinha em public/assets/ juntando as partes
../boneca_gc-1.mp4, ../boneca_gc-2.mp4, ... em ordem, com o fundo transparente.
O gerador de video da IA so faz 10s por vez, por isso a fala vem em partes. Para
acrescentar uma parte, salve o proximo numero na pasta e rode de novo.

    python arte/gerar-video.py        (rodar de dentro de frontend/)

Precisa, so na maquina de quem gera (nada disso vai para o deploy):

    pip install --user imageio-ffmpeg onnxruntime

O modelo de recorte (Robust Video Matting, ~100 MB) e baixado sozinho na primeira
vez para a pasta ~/.cache/convite-gc-styllus/.

Por que recorte por IA: o fundo do video e branco-gelo e a camiseta dela e branca,
quase da mesma cor. Tirar o fundo pela cor apagaria a camiseta. O modelo acerta
pessoa, mas erra a bolsa (a aba fica translucida), entao o que e bem colorido ou
escuro perto dela tambem fica opaco: o fundo e neutro e claro, nao ha confusao.

Sai:
- bonequinha.mp4: "EMPACOTADO", com o audio original. Cada quadro tem o dobro da
  largura, com a cor na metade esquerda e a transparencia (branco = opaco) na
  direita. src/services/videoBonequinha.js junta as metades num canvas. WebM com
  alfa nao serve: o Safari do iPhone mostra fundo preto.
- bonequinha-poster.webp: primeiro quadro, mostrado enquanto o video carrega.
- bonequinha-animado.webp: reserva de imagem, so baixada se o video falhar. Ha
  computador em que o decodificador de video da placa nao funciona, e celular em
  economia de bateria que bloqueia video automatico; imagem animada passa por
  esses dois casos.
- bonequinha-audio.m4a: so o som do video, tocado junto da imagem animada.

Ela esta FALANDO ate o fim de cada parte, entao a duracao nao muda (encurtar
cortaria a ultima palavra). So a imagem se funde: o comeco de cada parte com o
fim da anterior, e o finalzinho com o primeiro quadro, para a repeticao nao dar
um salto. O audio de cada parte e cortado na duracao exata dos quadros dela, para
a boca nao sair de sincronia nas emendas.

No fim, o script imprime onde cada parte comeca e os trechos com fala: e o que
serve para acertar os tempos das legendas em src/configuracaoTema.js.
"""
import os
import re
import subprocess
import urllib.request
import numpy as np
import imageio_ffmpeg
import onnxruntime as ort
from PIL import Image, ImageFilter

FRONTEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA_PARTES = os.path.dirname(FRONTEND)
PADRAO_PARTE = re.compile(r"^boneca_gc-(\d+)\.mp4$")
ASSETS = os.path.join(FRONTEND, "public", "assets")
DESTINO = os.path.join(ASSETS, "bonequinha.mp4")
POSTER = os.path.join(ASSETS, "bonequinha-poster.webp")
ANIMADO = os.path.join(ASSETS, "bonequinha-animado.webp")
AUDIO = os.path.join(ASSETS, "bonequinha-audio.m4a")

MODELO = os.path.join(os.path.expanduser("~"), ".cache", "convite-gc-styllus", "rvm_resnet50_fp32.onnx")
MODELO_URL = "https://github.com/PeterL1n/RobustVideoMatting/releases/download/v1.0.0/rvm_resnet50_fp32.onnx"
MODELO_ESCALA = 0.5  # resolucao em que o modelo olha o quadro
MODELO_AQUECIMENTO = 12  # repeticoes do 1o quadro: sem isso o comeco sai pior

FPS = 24
LARGURA, ALTURA = 720, 540
CRF = 23  # qualidade do H.264: menor = melhor e mais pesado
FUSAO_S = 0.5  # segundos finais em que a imagem se funde com o primeiro quadro
# Quadros do comeco de cada parte misturados com o fim da anterior. Fica em 0:
# o enquadramento muda de uma parte para outra (corpo inteiro / meio corpo) e a
# mistura mostrava as duas imagens sobrepostas. Corte seco parece edicao normal.
JUNCAO_QUADROS = 0
AUDIO_TAXA = 48000

# A reserva e baixada inteira: com a fala toda, ela precisa ser bem mais leve
ANIMADO_LARGURA, ANIMADO_ALTURA = 360, 270
ANIMADO_PULO = 3  # usa um quadro a cada 3 (8 fps)
ANIMADO_QUALIDADE = 60
ANIMADO_QUALIDADE_ALFA = 60

# Para imprimir os trechos com fala de cada parte
SILENCIO_DB = -35
SILENCIO_MIN_S = 0.2

# O que certamente nao e fundo. Saturacao = max(R,G,B) - min(R,G,B): o fundo fica
# perto de 10, e a bolsa, a saia e a pele bem acima. Escuro: o fundo nunca desce
# de ~200, nem nos cantos com vinheta, e o cabelo fica perto de 40.
SATURACAO_MIN, SATURACAO_MAX = 22, 45  # baixo o bastante para pegar a corrente dourada
ESCURO_MIN, ESCURO_MAX = 130, 170
# Essa regra so vale perto do que o modelo marcou como pessoa. A conta e feita em
# 1/8 da resolucao: 9 pixels de filtro la dao cerca de 36 pixels no quadro.
VIZINHANCA_FILTRO = 9
# Fundo verde: quanto o G passa de max(R, B). Pele, rosa, branco e dourado nunca
# passam; o fundo verde passa de longe.
VERDE_MIN, VERDE_MAX = 8, 28

# Cor que preenche a parte transparente da metade "cor". A compressao borra a cor
# vizinha para dentro da borda; sendo o rosa do fundo do hero, o borrao nao aparece.
COR_VAZIO = np.array([251, 220, 234], np.float32)


def ffmpeg():
    return imageio_ffmpeg.get_ffmpeg_exe()


def obter_modelo():
    if not os.path.exists(MODELO):
        os.makedirs(os.path.dirname(MODELO), exist_ok=True)
        print("baixando o modelo de recorte...")
        urllib.request.urlretrieve(MODELO_URL, MODELO + ".parcial")
        os.replace(MODELO + ".parcial", MODELO)
    return ort.InferenceSession(MODELO, providers=["CPUExecutionProvider"])


def listar_partes():
    numeros = {}
    for nome in os.listdir(PASTA_PARTES):
        achou = PADRAO_PARTE.match(nome)
        if achou:
            numeros[int(achou.group(1))] = os.path.join(PASTA_PARTES, nome)
    if not numeros:
        raise SystemExit(f"nenhum boneca_gc-1.mp4, boneca_gc-2.mp4... em {PASTA_PARTES}")
    faltam = [n for n in range(1, max(numeros) + 1) if n not in numeros]
    if faltam:
        raise SystemExit("faltam as partes " + ", ".join(f"boneca_gc-{n}.mp4" for n in faltam))
    return [numeros[n] for n in sorted(numeros)]


def ler_quadros(origem):
    sonda = subprocess.run([ffmpeg(), "-hide_banner", "-i", origem], capture_output=True,
                           text=True, encoding="utf-8", errors="replace").stderr
    w, h = map(int, re.search(r"Video:.*?(\d{2,5})x(\d{2,5})", sonda).groups())
    # Recorte 4:3 no centro: ela fica centralizada e os bracos abertos cabem.
    # Na resolucao original: o recorte enxerga melhor e so depois a imagem reduz.
    corte = round(h * 4 / 3)
    x = (w - corte) // 2
    bruto = subprocess.run(
        [ffmpeg(), "-v", "error", "-i", origem,
         "-vf", f"fps={FPS},crop={corte}:{h}:{x}:0",
         "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        capture_output=True, check=True,
    ).stdout
    return np.frombuffer(bruto, np.uint8).reshape(-1, h, corte, 3)


def verde_de_fundo(q):
    """0 a 1: quanto o verde passa do vermelho e do azul (fundo verde)."""
    sobra = q[..., 1] - np.maximum(q[..., 0], q[..., 2])
    return np.clip((sobra - VERDE_MIN) / (VERDE_MAX - VERDE_MIN), 0, 1)


def certamente_figura(quadro, alfa_modelo):
    """Rampa de 0 a 1 para o que nao pode ser fundo, so perto da pessoa."""
    q = quadro.astype(np.float32)
    saturacao = q.max(axis=2) - q.min(axis=2)
    brilho = q.max(axis=2)
    colorido = np.clip((saturacao - SATURACAO_MIN) / (SATURACAO_MAX - SATURACAO_MIN), 0, 1)
    escuro = np.clip((ESCURO_MAX - brilho) / (ESCURO_MAX - ESCURO_MIN), 0, 1)

    h, w = alfa_modelo.shape
    pessoa = Image.fromarray(((alfa_modelo > 0.5) * 255).astype(np.uint8)).resize((w // 8, h // 8), Image.BILINEAR)
    perto = pessoa.filter(ImageFilter.MaxFilter(VIZINHANCA_FILTRO)).resize((w, h), Image.BILINEAR)
    # Ha parte gravada em fundo verde, que e colorido e escuro: verde forte e
    # sempre fundo, nunca roupa dela
    nao_verde = 1 - verde_de_fundo(q)
    return np.maximum(colorido, escuro) * nao_verde * (np.asarray(perto, np.float32) / 255)


def recortar(quadro, cor_modelo, alfa_modelo):
    extra = certamente_figura(quadro, alfa_modelo)
    alfa = np.maximum(alfa_modelo, extra)
    # O modelo devolve a cor sem o fundo misturado, o que tira o halo claro do
    # cabelo. So nao vale onde ele achou que era fundo: ali a cor verdadeira e a
    # do proprio video.
    usa_original = np.clip((extra - alfa_modelo) * 4, 0, 1)[..., None]
    cor = cor_modelo * 255 * (1 - usa_original) + quadro.astype(np.float32) * usa_original
    # Tira o reflexo do fundo verde na borda do cabelo e da pele (G nunca acima
    # de R e B). Nas cores dela o G ja fica abaixo, entao nada muda.
    cor[..., 1] = np.minimum(cor[..., 1], np.maximum(cor[..., 0], cor[..., 2]))
    cor = np.where(alfa[..., None] > 0.01, cor, COR_VAZIO)
    return (
        np.array(Image.fromarray(np.clip(cor, 0, 255).astype(np.uint8)).resize((LARGURA, ALTURA), Image.LANCZOS)),
        np.array(Image.fromarray((alfa * 255).astype(np.uint8)).resize((LARGURA, ALTURA), Image.LANCZOS)),
    )


def recortar_parte(sessao, quadros):
    # Memoria do modelo zerada a cada parte: cada uma foi gerada separada, e o
    # que ele lembra da anterior atrapalharia o comeco da seguinte.
    memoria = [np.zeros([1, 1, 1, 1], np.float32) for _ in range(4)]
    escala = np.array([MODELO_ESCALA], np.float32)

    def passo(q):
        nonlocal memoria
        cor, alfa, *memoria = sessao.run(None, {
            "src": (q.astype(np.float32) / 255).transpose(2, 0, 1)[None],
            "r1i": memoria[0], "r2i": memoria[1], "r3i": memoria[2], "r4i": memoria[3],
            "downsample_ratio": escala,
        })
        return cor[0].transpose(1, 2, 0), alfa[0, 0]

    for _ in range(MODELO_AQUECIMENTO):
        passo(quadros[0])
    for q in quadros:
        yield recortar(q, *passo(q))


def fundir(cor_a, alfa_a, cor_b, alfa_b, peso):
    """Mistura dois quadros com transparencia sem a cor do vazio manchar a borda."""
    a = alfa_a.astype(np.float32)[..., None] * (1 - peso)
    b = alfa_b.astype(np.float32)[..., None] * peso
    soma = a + b
    with np.errstate(divide="ignore", invalid="ignore"):
        cor = np.where(soma > 0, (cor_a * a + cor_b * b) / soma, COR_VAZIO)
    return np.clip(cor, 0, 255).astype(np.uint8), soma[..., 0].astype(np.uint8)


def juntar_audio(partes, quadros_por_parte, video_sem_audio):
    """Poe o audio das partes, cada um cortado na duracao exata dos seus quadros."""
    entradas = ["-i", video_sem_audio]
    filtros = []
    for i, (parte, n) in enumerate(zip(partes, quadros_por_parte), start=1):
        entradas += ["-i", parte]
        filtros.append(f"[{i}:a]aresample={AUDIO_TAXA},apad,atrim=end={n / FPS:.6f},asetpts=PTS-STARTPTS[a{i}]")
    rotulos = "".join(f"[a{i}]" for i in range(1, len(partes) + 1))
    filtros.append(f"{rotulos}concat=n={len(partes)}:v=0:a=1[a]")
    subprocess.run(
        [ffmpeg(), "-v", "error", "-y", *entradas, "-filter_complex", ";".join(filtros),
         "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "96k",
         "-movflags", "+faststart", DESTINO],
        check=True,
    )


def trechos_com_fala(parte):
    saida = subprocess.run(
        [ffmpeg(), "-hide_banner", "-i", parte, "-vn",
         "-af", f"silencedetect=noise={SILENCIO_DB}dB:d={SILENCIO_MIN_S}", "-f", "null", "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    ).stderr
    duracao = re.search(r"Duration: (\d+):(\d+):([\d.]+)", saida)
    fim_total = int(duracao.group(1)) * 3600 + int(duracao.group(2)) * 60 + float(duracao.group(3))
    inicios = [float(s) for s in re.findall(r"silence_start: ([\d.]+)", saida)]
    fins = [float(s) for s in re.findall(r"silence_end: ([\d.]+)", saida)]
    trechos, cursor = [], 0.0
    for i, ini in enumerate(inicios):
        if ini > cursor:
            trechos.append((cursor, ini))
        cursor = fins[i] if i < len(fins) else fim_total
    if cursor < fim_total:
        trechos.append((cursor, fim_total))
    return trechos


def gerar():
    partes = listar_partes()
    sessao = obter_modelo()
    fusao = round(FUSAO_S * FPS)
    sem_audio = DESTINO + ".sem-audio.mp4"

    proc = subprocess.Popen(
        [ffmpeg(), "-v", "error", "-y",
         "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{LARGURA * 2}x{ALTURA}", "-r", str(FPS), "-i", "-",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", str(CRF), "-preset", "slow", sem_audio],
        stdin=subprocess.PIPE,
    )
    animado = []
    primeiro = None
    anterior = None  # ultimo quadro da parte anterior, para a emenda
    quadros_por_parte = []
    i = 0
    for p, parte in enumerate(partes):
        print(f"recortando {os.path.basename(parte)}...", flush=True)
        quadros = ler_quadros(parte)
        quadros_por_parte.append(len(quadros))
        ultima = p == len(partes) - 1
        for j, (cor, alfa) in enumerate(recortar_parte(sessao, quadros)):
            if primeiro is None:
                primeiro = (cor, alfa)
            if anterior is not None and j < JUNCAO_QUADROS:
                cor, alfa = fundir(*anterior, cor, alfa, (j + 1) / (JUNCAO_QUADROS + 1))
            faltam = len(quadros) - j
            if ultima and faltam <= fusao:
                cor, alfa = fundir(cor, alfa, *primeiro, 1 - (faltam - 1) / fusao)
            proc.stdin.write(np.concatenate([cor, np.repeat(alfa[..., None], 3, axis=2)], axis=1).tobytes())
            if i % ANIMADO_PULO == 0:
                rgba = Image.fromarray(np.dstack([cor, alfa]))
                animado.append(rgba.resize((ANIMADO_LARGURA, ANIMADO_ALTURA), Image.LANCZOS))
            i += 1
            if faltam == 1:
                anterior = (cor, alfa)
        del quadros
    proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit("o ffmpeg falhou ao gerar o video")

    juntar_audio(partes, quadros_por_parte, sem_audio)
    os.remove(sem_audio)

    subprocess.run(
        [ffmpeg(), "-v", "error", "-y", "-i", DESTINO, "-vn", "-c:a", "copy", "-movflags", "+faststart", AUDIO],
        check=True,
    )

    Image.fromarray(np.dstack(primeiro)).save(POSTER, "WEBP", quality=82, method=6)
    animado[0].save(
        ANIMADO, "WEBP", save_all=True, append_images=animado[1:],
        duration=round(1000 * ANIMADO_PULO / FPS), loop=0,
        quality=ANIMADO_QUALIDADE, alpha_quality=ANIMADO_QUALIDADE_ALFA, method=4,
    )

    print(f"\n{i} quadros a {FPS} fps ({i / FPS:.2f}s)")
    for arq in (DESTINO, POSTER, ANIMADO, AUDIO):
        print(f"{os.path.basename(arq)}: {os.path.getsize(arq) / 1024:.0f} KB")

    print("\nTempos no video final (para as legendas):")
    inicio = 0.0
    for parte, n in zip(partes, quadros_por_parte):
        fala = ", ".join(f"{inicio + a:.2f}-{inicio + min(b, n / FPS):.2f}"
                         for a, b in trechos_com_fala(parte) if a < n / FPS)
        print(f"  {os.path.basename(parte)}: comeca em {inicio:.2f}s | fala: {fala}")
        inicio += n / FPS


if __name__ == "__main__":
    os.makedirs(ASSETS, exist_ok=True)
    gerar()
