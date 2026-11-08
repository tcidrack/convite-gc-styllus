# Convite: Inauguração da GC STYLLUS

Convite digital em Vite + React, no mesmo padrão do `convite-thayla`.

## Rodar

```bash
cd frontend
npm install
npm run dev      # http://localhost:5173
npm run build    # gera dist/
```

## Rotas

| Rota | O que é |
|---|---|
| `/` | Envelope; ao tocar, sobe o cartão com a logo e abre o convite |
| `/convite` | Primeira tela: vídeo, data, 3 destaques, local e confirmar presença. O restante aparece na janela depois de confirmar |
| `/admin` | Lista de quem confirmou presença (pede senha) |

## Editar os dados

Tudo fica em `frontend/src/configuracaoTema.js`, nos pontos marcados com `<< EDITE AQUI >>`.

## Imagens

A fala da bonequinha vem em partes de 10s (o gerador de vídeo por IA não faz mais que isso): `boneca_gc-1.mp4`, `boneca_gc-2.mp4`... na raiz do projeto, na ordem em que ela fala. Elas não vão para o deploy, só o vídeo final. Para trocar uma parte ou acrescentar a próxima, salve o arquivo com o número certo e rode, de dentro de `frontend/`:

```bash
pip install --user imageio-ffmpeg onnxruntime   # uma vez só
python arte/gerar-video.py
```

Na primeira vez o script baixa o modelo de recorte por IA (cerca de 100 MB) para `~/.cache/convite-gc-styllus/`. Ele e o `onnxruntime` só servem para gerar o vídeo e não vão para o deploy.

O script junta as partes num vídeo só, com o fundo tirado (vale também para parte gravada em fundo verde). Sai o vídeo, a imagem parada, uma imagem animada de reserva e o áudio separado: se o vídeo não puder tocar (há computador em que a placa de vídeo não decodifica), entram a imagem animada e o áudio. O MP4 tem o dobro da largura, com a cor à esquerda e a transparência à direita; o site junta as duas metades num canvas, o que funciona também no iPhone. Por isso o arquivo parece estranho se aberto fora do site.

O som tenta ligar no toque do envelope e toca a fala uma vez; depois o vídeo repete mudo e o botão "Ouvir de novo" recomeça do início com som (`src/services/videoBonequinha.js`).

### Legendas

Ficam em `frontend/src/configuracaoTema.js`, em `recursos.legendas`, com início e fim em segundos do vídeo inteiro (a parte 2 começa em 10, a 3 em 20...). Ao acrescentar uma parte, o script imprime no fim os trechos com fala de cada uma: use esses tempos para as frases novas. Se uma frase aparecer adiantada ou atrasada, é só ajustar os números.

O navegador pode guardar o vídeo antigo depois de gerar um novo: recarregue com Ctrl+F5.

A logo é desenhada em código (`src/componentes/Logo.jsx`).

## Confirmação de presença (Supabase)

O `.env` aponta para o mesmo projeto Supabase dos outros convites. Todos os objetos do banco têm o sufixo `gc_styllus`, para não mexer neles.

1. No `database.sql`, troque `TROQUE_ESTA_SENHA` (bloco 6) pela senha da `/admin`.
2. Rode o script no SQL Editor do Supabase.

Enquanto o script não for rodado, a confirmação fica salva só no navegador do convidado e não aparece na `/admin`.

## Publicar (Vercel)

O projeto `convite-gc-styllus` da Vercel está ligado a este repositório, com `frontend` como pasta raiz e as chaves `VITE_SUPABASE_URL` e `VITE_SUPABASE_ANON_KEY` cadastradas. Cada push na `main` publica sozinho.

Pendente: adicionar `og:image` no `index.html`, com o endereço completo de uma imagem, para a prévia no WhatsApp.
