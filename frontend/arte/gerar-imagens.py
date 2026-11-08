# -*- coding: utf-8 -*-
"""
Gera o favicon de public/, com o monograma GC.

    python arte/gerar-imagens.py        (rodar de dentro de frontend/)

O video da bonequinha e as imagens ligadas a ele saem de arte/gerar-video.py.
"""
import os
from PIL import Image, ImageDraw, ImageFont

FRONTEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def gerar_favicon():
    # Desenha grande e reduz, para a borda ficar suave.
    lado = 512
    img = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((8, 8, lado - 8, lado - 8), fill="#C9A24D")
    d.ellipse((30, 30, lado - 30, lado - 30), fill="#D1126F")
    fonte = ImageFont.truetype("C:/Windows/Fonts/georgiab.ttf", 230)
    d.text((lado / 2, lado / 2), "GC", font=fonte, fill="#FFFFFF", anchor="mm")
    img.resize((128, 128), Image.LANCZOS).save(os.path.join(FRONTEND, "public", "favicon.png"))
    print("favicon.png (128, 128)")


if __name__ == "__main__":
    gerar_favicon()
