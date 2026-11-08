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

Fala repetida pela IA sai com CORTES (mais abaixo), em quadros da parte.

No fim, o script grava src/partesVideo.js (onde cada parte comeca e os cortes)
e imprime os trechos com fala. As legendas de src/configuracaoTema.js contam do
comeco de cada parte, no arquivo original: cortar ou trocar uma parte nao
desloca as legendas das outras.
"""
import itertools
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
# boneca_gc-3.mp4, e boneca_gc-3b.mp4 para uma fala dividida em dois videos
PADRAO_PARTE = re.compile(r"^boneca_gc-(\d+)([a-z]?)\.mp4$")
ASSETS = os.path.join(FRONTEND, "public", "assets")
DESTINO = os.path.join(ASSETS, "bonequinha.mp4")
POSTER = os.path.join(ASSETS, "bonequinha-poster.webp")
ANIMADO = os.path.join(ASSETS, "bonequinha-animado.webp")
AUDIO = os.path.join(ASSETS, "bonequinha-audio.m4a")
# Onde cada parte comeca no video final, lido pelas legendas (src/legendas.js)
PARTES_JS = os.path.join(FRONTEND, "src", "partesVideo.js")

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

# Trechos tirados de uma parte (fala repetida pela IA), em quadros a 24 fps a
# partir do comeco da parte, com o fim de fora. Corte sempre num silencio.
CORTES = {
    "2": [(185, 202)],  # "e muito e muito mimos" -> "e muito mimos"
    "3": [(238, 246)],  # "slim" + um "to" solto no fim -> "slim"
}
# Trechos de uma parte trocados por fala de outro video, quando a IA engole uma
# palavra numa frase longa mas fala direito sozinha. (quadro inicial, quadro
# final de fora, arquivo na pasta das partes, inicio e fim em segundos nele). A
# imagem do trecho e esticada ate a duracao da fala nova, para a boca nao parar
# antes da voz. Com "imagem" no fim, a imagem tambem vem do outro video (a boca
# bate; fica um corte de cena). As emendas ficam em silencios dos dois lados.
TROCAS = {
    "3": [
        (44, 54, "dez.mp4", 17.58, 18.66),  # "[...] por cento" -> "dez por cento"
        (109, 137, "vinte-e-um.mp4", 24.52, 27.80),  # "do dia vin vinte oito" -> "do dia vinte e um ao dia vinte e oito"
    ],
}
EMENDA_S = 0.01  # fade do audio em cada emenda, para nao estalar

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


def nome_parte(parte):
    """boneca_gc-3b.mp4 -> "3b": o nome usado nos CORTES e nas legendas."""
    achou = PADRAO_PARTE.match(os.path.basename(parte))
    return achou.group(1) + achou.group(2)


def listar_partes():
    achadas = {}
    for nome in os.listdir(PASTA_PARTES):
        achou = PADRAO_PARTE.match(nome)
        if achou:
            achadas[(int(achou.group(1)), achou.group(2))] = os.path.join(PASTA_PARTES, nome)
    if not achadas:
        raise SystemExit(f"nenhum boneca_gc-1.mp4, boneca_gc-2.mp4... em {PASTA_PARTES}")
    numeros = {n for n, _ in achadas}
    faltam = [n for n in range(1, max(numeros) + 1) if n not in numeros]
    if faltam:
        raise SystemExit("faltam as partes " + ", ".join(f"boneca_gc-{n}.mp4" for n in faltam))
    return [achadas[k] for k in sorted(achadas)]


def pedacos(parte, total):
    """A parte em ordem: ("parte", a, b) mantem os quadros [a, b); ("outro", a, b,
    arquivo, ini, n, com_imagem) poe n quadros com a fala do outro arquivo no lugar
    de [a, b), com a imagem de [a, b) esticada ou, com_imagem, a do outro arquivo.
    O que cai nos CORTES some."""
    nome = nome_parte(parte)
    marcas = [(a, b, None) for a, b in CORTES.get(nome, [])]
    for a, b, arquivo, ini, fim, *resto in TROCAS.get(nome, []):
        marcas.append((a, b, (arquivo, ini, round((fim - ini) * FPS), "imagem" in resto)))
    lista, cursor = [], 0
    for a, b, outro in sorted(marcas):
        if a > cursor:
            lista.append(("parte", cursor, a))
        if outro:
            lista.append(("outro", a, b, *outro))
        cursor = max(cursor, b)
    if cursor < total:
        lista.append(("parte", cursor, total))
    return lista


def mapa_da_parte(parte, total):
    """Para cada quadro de saida, o indice do quadro original que ele mostra."""
    mapa = []
    for p in pedacos(parte, total):
        if p[0] == "parte":
            mapa.extend(range(p[1], p[2]))
        else:
            _, a, b, _, _, n, com_imagem = p
            mapa.extend([None] * n if com_imagem else (a + k * (b - a) // n for k in range(n)))
    return mapa


def medidas(origem):
    """Filtro do recorte 4:3 no centro e o tamanho do quadro que ele entrega."""
    sonda = subprocess.run([ffmpeg(), "-hide_banner", "-i", origem], capture_output=True,
                           text=True, encoding="utf-8", errors="replace").stderr
    w, h = map(int, re.search(r"Video:.*?(\d{2,5})x(\d{2,5})", sonda).groups())
    # Recorte 4:3 no centro: ela fica centralizada e os bracos abertos cabem.
    # Na resolucao original: o recorte enxerga melhor e so depois a imagem reduz.
    corte = round(h * 4 / 3)
    return f"fps={FPS},crop={corte}:{h}:{(w - corte) // 2}:0", corte, h


def contar_quadros(parte):
    """Quadros da parte a 24 fps, antes dos CORTES, sem guardar nenhum."""
    filtro, _, _ = medidas(parte)
    saida = subprocess.run([ffmpeg(), "-hide_banner", "-i", parte, "-an", "-vf", filtro, "-f", "null", "-"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    return int(re.findall(r"frame=\s*(\d+)", saida)[-1])


def ler_fluxo(origem, filtro, w, h, *antes):
    """Quadros de um video, um por vez, ja com o filtro do recorte."""
    proc = subprocess.Popen([ffmpeg(), "-v", "error", *antes, "-i", origem, "-vf", filtro,
                             "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    tamanho = w * h * 3
    try:
        while True:
            bruto = proc.stdout.read(tamanho)
            if len(bruto) < tamanho:
                return
            yield np.frombuffer(bruto, np.uint8).reshape(h, w, 3)
    finally:
        proc.stdout.close()
        proc.kill()
        proc.wait()


def quadros_da_parte(parte, total=None):
    """Entrega um quadro por vez, seguindo os pedacos (cortes, trechos esticados e
    imagem de outro video): a parte inteira na memoria passava de 1 GB e o
    Windows derrubava o processo."""
    total = total if total is not None else contar_quadros(parte)
    filtro, w, h = medidas(parte)
    principal = ler_fluxo(parte, filtro, w, h)
    lido, atual, anterior = -1, None, None

    def quadro(indice):
        """O quadro `indice` do original; guarda tambem o anterior, que a mistura
        do trecho esticado pede depois de ja ter lido o seguinte."""
        nonlocal lido, atual, anterior
        while lido < indice:
            proximo = next(principal, None)
            if proximo is None:
                break
            anterior, atual, lido = atual, proximo, lido + 1
        return anterior if indice == lido - 1 and anterior is not None else atual

    try:
        for p in pedacos(parte, total):
            if p[0] == "parte":
                for k in range(p[1], p[2]):
                    yield quadro(k)
            elif not p[6]:
                # Imagem original esticada ate a duracao da fala nova: cada quadro
                # mistura os dois originais vizinhos, para a camera lenta nao travar
                _, a, b, _, _, n, _ = p
                for k in range(n):
                    pos = min(max(a + (k + 0.5) * (b - a) / n - 0.5, a), b - 1)
                    base = int(pos)
                    peso = pos - base
                    seguinte = quadro(base + 1) if peso > 0.01 else None
                    q = quadro(base)
                    if seguinte is None:
                        yield q
                    else:
                        yield (q.astype(np.float32) * (1 - peso) + seguinte.astype(np.float32) * peso + 0.5).astype(np.uint8)
            else:
                _, _, _, arquivo, ini, n, _ = p
                caminho = os.path.join(PASTA_PARTES, arquivo)
                filtro_outro, w2, h2 = medidas(caminho)
                if (w2, h2) != (w, h):
                    raise SystemExit(f"{arquivo} tem outro tamanho de quadro que {os.path.basename(parte)}")
                ultimo = None
                outro = ler_fluxo(caminho, filtro_outro, w, h, "-ss", f"{ini:.3f}", "-t", f"{n / FPS + 0.5:.3f}")
                for k in range(n):
                    ultimo = next(outro, ultimo)
                    yield ultimo
                outro.close()
    finally:
        principal.close()


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

    quadros = iter(quadros)
    primeiro = next(quadros)
    for _ in range(MODELO_AQUECIMENTO):
        passo(primeiro)
    for q in itertools.chain([primeiro], quadros):
        yield recortar(q, *passo(q))


def fundir(cor_a, alfa_a, cor_b, alfa_b, peso):
    """Mistura dois quadros com transparencia sem a cor do vazio manchar a borda."""
    a = alfa_a.astype(np.float32)[..., None] * (1 - peso)
    b = alfa_b.astype(np.float32)[..., None] * peso
    soma = a + b
    with np.errstate(divide="ignore", invalid="ignore"):
        cor = np.where(soma > 0, (cor_a * a + cor_b * b) / soma, COR_VAZIO)
    return np.clip(cor, 0, 255).astype(np.uint8), soma[..., 0].astype(np.uint8)


def volume_da_fala(arquivo, ini, dur):
    """dB medio so dos trechos com voz (acima de -40 dB, em janelas de 20 ms)."""
    bruto = subprocess.run([ffmpeg(), "-v", "error", "-ss", f"{max(ini, 0):.3f}", "-t", f"{dur:.3f}", "-i", arquivo,
                            "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True).stdout
    x = np.frombuffer(bruto, np.int16).astype(np.float32) / 32768
    janelas = x[:len(x) // 320 * 320].reshape(-1, 320)
    db = 20 * np.log10(np.sqrt((janelas ** 2).mean(axis=1)) + 1e-9)
    voz = janelas[db > -40]
    return 20 * np.log10(np.sqrt((voz ** 2).mean()) + 1e-9) if len(voz) else -20.0


def audio_da_parte(i, parte, total, n, entrada):
    """Filtro do audio de uma parte: tira os CORTES, poe as TROCAS e acerta na
    duracao dos quadros. `entrada(arquivo)` devolve o numero do -i do arquivo."""
    fim = f"apad,atrim=end={n / FPS:.6f},asetpts=PTS-STARTPTS[a{i}]"
    lista = pedacos(parte, total)
    if lista == [("parte", 0, total)]:
        return f"[{i}:a]aresample={AUDIO_TAXA},{fim}"
    da_parte = [p for p in lista if p[0] == "parte"]
    filtros = [f"[{i}:a]aresample={AUDIO_TAXA},asplit={len(da_parte)}" + "".join(f"[s{i}_{k}]" for k in range(len(da_parte)))]
    rotulos, k_parte = [], 0
    for k, p in enumerate(lista):
        fades = []
        if k > 0:
            fades.append(f"afade=t=in:d={EMENDA_S}")
        if p[0] == "parte":
            _, a, b = p
            dur = (b - a) / FPS
            origem = f"[s{i}_{k_parte}]atrim={a / FPS:.6f}:{b / FPS:.6f},asetpts=PTS-STARTPTS"
            k_parte += 1
        else:
            _, a, _, arquivo, ini, m, _ = p
            caminho = os.path.join(PASTA_PARTES, arquivo)
            dur = m / FPS
            ganho = volume_da_fala(parte, a / FPS - 1.5, 1.5) - volume_da_fala(caminho, ini, dur)
            origem = (f"[{entrada(caminho)}:a]aresample={AUDIO_TAXA},atrim={ini:.6f}:{ini + dur:.6f},"
                      f"asetpts=PTS-STARTPTS,volume={ganho:.2f}dB,apad,atrim=end={dur:.6f}")
        if k < len(lista) - 1:
            fades.append(f"afade=t=out:st={dur - EMENDA_S:.6f}:d={EMENDA_S}")
        filtros.append(origem + "".join("," + f for f in fades) + f"[c{i}_{k}]")
        rotulos.append(f"[c{i}_{k}]")
    filtros.append("".join(rotulos) + f"concat=n={len(lista)}:v=0:a=1,{fim}")
    return ";".join(filtros)


def juntar_audio(partes, totais, quadros_por_parte, video_sem_audio):
    """Poe o audio das partes, cada um cortado na duracao exata dos seus quadros."""
    entradas = ["-i", video_sem_audio]
    for parte in partes:
        entradas += ["-i", parte]
    extras = {}

    def entrada(arquivo):
        if arquivo not in extras:
            extras[arquivo] = len(partes) + 1 + len(extras)
        return extras[arquivo]

    filtros = [audio_da_parte(i, parte, total, n, entrada)
               for i, (parte, total, n) in enumerate(zip(partes, totais, quadros_por_parte), start=1)]
    for arquivo in extras:
        entradas += ["-i", arquivo]
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


def gravar_partes_js(partes, totais, quadros_por_parte):
    inicios, trechos, inicio = [], [], 0
    for parte, total, n in zip(partes, totais, quadros_por_parte):
        nome = nome_parte(parte)
        inicios.append(f'  "{nome}": {inicio / FPS:.4f},')
        inicio += n
        # trechos que mudam o tempo: cortes (somem) e trocas (esticam)
        lista, saida, cursor = [], 0, 0
        for p in pedacos(parte, total):
            a, b = p[1], p[2]
            if a > cursor:  # corte antes deste pedaco
                lista.append(f"[{cursor / FPS:.4f}, {a / FPS:.4f}, {saida / FPS:.4f}, {saida / FPS:.4f}]")
            if p[0] == "parte":
                saida += b - a
            else:
                lista.append(f"[{a / FPS:.4f}, {b / FPS:.4f}, {saida / FPS:.4f}, {(saida + p[5]) / FPS:.4f}]")
                saida += p[5]
            cursor = b
        if cursor < total:  # corte no fim da parte
            lista.append(f"[{cursor / FPS:.4f}, {total / FPS:.4f}, {saida / FPS:.4f}, {saida / FPS:.4f}]")
        if lista:
            trechos.append(f'  "{nome}": [{", ".join(lista)}],')
    with open(PARTES_JS, "w", encoding="utf-8", newline="\n") as f:
        f.write("// Gerado por arte/gerar-video.py: nao edite a mao.\n"
                "// Segundo do video final em que cada parte comeca.\n"
                "export const INICIO_PARTES = {\n" + "\n".join(inicios) + "\n}\n\n"
                "// Trechos de cada parte que mudam de duracao (CORTES e TROCAS), em segundos:\n"
                "// [inicio, fim] no arquivo original da parte -> [inicio, fim] na parte ja montada.\n"
                "export const TRECHOS = {\n" + "\n".join(trechos) + "\n}\n")


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
    totais = []  # quadros de cada parte antes dos CORTES
    i = 0
    for p, parte in enumerate(partes):
        print(f"recortando {os.path.basename(parte)}...", flush=True)
        total = contar_quadros(parte)
        n = len(mapa_da_parte(parte, total))
        totais.append(total)
        quadros_por_parte.append(n)
        ultima = p == len(partes) - 1
        for j, (cor, alfa) in enumerate(recortar_parte(sessao, quadros_da_parte(parte, total))):
            if primeiro is None:
                primeiro = (cor, alfa)
            if anterior is not None and j < JUNCAO_QUADROS:
                cor, alfa = fundir(*anterior, cor, alfa, (j + 1) / (JUNCAO_QUADROS + 1))
            faltam = n - j
            if ultima and faltam <= fusao:
                cor, alfa = fundir(cor, alfa, *primeiro, 1 - (faltam - 1) / fusao)
            proc.stdin.write(np.concatenate([cor, np.repeat(alfa[..., None], 3, axis=2)], axis=1).tobytes())
            if i % ANIMADO_PULO == 0:
                rgba = Image.fromarray(np.dstack([cor, alfa]))
                animado.append(rgba.resize((ANIMADO_LARGURA, ANIMADO_ALTURA), Image.LANCZOS))
            i += 1
            if faltam == 1:
                anterior = (cor, alfa)
    proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit("o ffmpeg falhou ao gerar o video")

    juntar_audio(partes, totais, quadros_por_parte, sem_audio)
    gravar_partes_js(partes, totais, quadros_por_parte)
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

    print("\nPara as legendas (segundos dentro de cada parte, no arquivo original):")
    inicio = 0.0
    for parte, n in zip(partes, quadros_por_parte):
        fala = ", ".join(f"{a:.2f}-{b:.2f}" for a, b in trechos_com_fala(parte))
        print(f"  parte '{nome_parte(parte)}' (comeca em {inicio:.2f}s do video): fala {fala}")
        inicio += n / FPS


if __name__ == "__main__":
    os.makedirs(ASSETS, exist_ok=True)
    gerar()
