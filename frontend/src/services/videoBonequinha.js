import { tema } from '../configuracaoTema'

// Um unico <video> para o site inteiro, criado fora dos componentes de proposito.
// Celular so deixa tocar com som um video que recebeu play() de dentro de um
// toque. O toque e no envelope, mas o video so aparece depois, na troca para
// /convite: por isso e o mesmo elemento nas duas telas, ja liberado.
//
// O MP4 vem "empacotado" (arte/gerar-video.py): metade esquerda e a cor, metade
// direita e a transparencia em tons de cinza (branco = opaco). O video fica
// escondido, tocando e dando o som, e um canvas junta as metades a cada quadro.
// WebM com alfa nao tem transparencia no Safari do iPhone.

// Escondido, mas sem display:none: o Safari do iPhone para de decodificar
// quadros de um <video> que nao esta visivel na pagina.
const VIDEO_ESCONDIDO = {
  position: 'absolute',
  width: '1px',
  height: '1px',
  opacity: '0',
  pointerEvents: 'none',
}

let video = null
let querSom = false // pediu som ao abrir: vale para a primeira passada
let exibindo = false
let pausadoPelaAba = false
let falhou = false
let audio = null // so o som, para quando o video nao toca e entra a imagem animada
let exibindoReserva = false
const ouvintes = new Set()

function avisar() {
  const mudo = falhou ? !audio || audio.paused : !video || video.muted
  ouvintes.forEach((fn) => fn({ falhou, mudo }))
}

function marcarFalha() {
  falhou = true
  avisar()
}

function obterVideo() {
  if (video) return video

  video = document.createElement('video')
  Object.assign(video.style, VIDEO_ESCONDIDO)
  video.src = tema.recursos.video
  video.muted = true
  video.preload = 'auto'
  // O iPhone so aceita tocar dentro da pagina com o atributo no HTML
  video.setAttribute('playsinline', '')
  video.setAttribute('aria-hidden', 'true')

  video.addEventListener('volumechange', avisar)
  video.addEventListener('error', marcarFalha)

  // Sem `loop`: o fim do video e o que marca o fim de uma passada com som.
  video.addEventListener('ended', () => {
    querSom = false
    video.muted = true
    video.currentTime = 0
    tocar()
  })

  document.addEventListener('visibilitychange', () => {
    if (!exibindo) return
    if (document.hidden && !video.paused) {
      pausadoPelaAba = true
      video.pause()
    } else if (!document.hidden && pausadoPelaAba) {
      pausadoPelaAba = false
      tocar()
    }
  })

  return video
}

// Toca como estiver; se o navegador recusar o som, tenta de novo mudo. Recusar
// ate mudo e o modo economia de bateria: ai entra a imagem animada de reserva.
function tocar() {
  return video.play().catch((erro) => {
    if (!erro || erro.name !== 'NotAllowedError') return
    if (video.muted) {
      marcarFalha()
      return
    }
    querSom = false
    video.muted = true
    return video.play().catch(marcarFalha)
  })
}

function obterAudio() {
  if (audio) return audio

  audio = new Audio(tema.recursos.audioReserva)
  audio.preload = 'auto'
  audio.addEventListener('play', avisar)
  audio.addEventListener('pause', avisar)
  audio.addEventListener('ended', () => {
    querSom = false
    avisar()
  })
  return audio
}

function tocarAudio() {
  const a = obterAudio()
  a.volume = 1
  a.currentTime = 0
  return a.play().catch(avisar)
}

// Igual ao video: o audio de reserva tambem precisa receber play() dentro do
// toque, porque so se sabe depois se o video vai falhar.
function liberarAudio() {
  const a = obterAudio()
  a.volume = 0
  a.play().then(
    () => {
      if (exibindoReserva) return
      a.pause()
      a.currentTime = 0
    },
    () => {}
  )
}

export function preCarregar() {
  obterVideo()
}

// Tem que ser chamado de dentro do toque no envelope. So libera: o video volta
// para o inicio e comeca a valer quando o convite aparecer, para a fala nao
// comecar escondida atras do envelope. O volume zero evita um estalo de som
// durante esse instante (o iPhone ignora o volume, mas la e bem curto).
export function liberarSom() {
  const v = obterVideo()
  querSom = true
  v.muted = false
  v.volume = 0
  liberarAudio()
  const tentativa = v.play()
  if (!tentativa || !tentativa.then) return
  tentativa.then(
    () => {
      if (exibindo) return
      v.pause()
      v.currentTime = 0
    },
    (erro) => {
      // Ser interrompido por um pause() nao e recusa: so o navegador negar desliga o som
      if (!erro || erro.name !== 'NotAllowedError') return
      querSom = false
      v.muted = true
    }
  )
}

// Desenha o video no canvas a cada quadro novo. Devolve a funcao que para.
function desenharSemFundo(v, canvas, aoComecar) {
  const ctx = canvas.getContext('2d')
  const auxiliar = document.createElement('canvas')
  const ctxAux = auxiliar.getContext('2d', { willReadFrequently: true })
  let ativo = true
  let saida = null

  function agendar() {
    if (!ativo) return
    if (v.requestVideoFrameCallback) v.requestVideoFrameCallback(desenhar)
    else requestAnimationFrame(desenhar)
  }

  function desenhar() {
    if (!ativo) return
    const largura = v.videoWidth / 2
    const altura = v.videoHeight
    if (largura && v.readyState >= 2) {
      if (!saida) {
        canvas.width = largura
        canvas.height = altura
        auxiliar.width = largura * 2
        auxiliar.height = altura
        saida = ctx.createImageData(largura, altura)
      }
      ctxAux.drawImage(v, 0, 0)
      const dados = ctxAux.getImageData(0, 0, largura * 2, altura).data
      const px = saida.data
      const linha = largura * 4
      for (let y = 0; y < altura; y++) {
        const origem = y * linha * 2
        const destino = y * linha
        for (let x = 0; x < linha; x += 4) {
          px[destino + x] = dados[origem + x]
          px[destino + x + 1] = dados[origem + x + 1]
          px[destino + x + 2] = dados[origem + x + 2]
          px[destino + x + 3] = dados[origem + linha + x]
        }
      }
      ctx.putImageData(saida, 0, 0)
      aoComecar()
    }
    agendar()
  }

  agendar()
  return () => {
    ativo = false
  }
}

// Coloca a imagem no lugar dela na pagina e comeca. A imagem parada aparece ate
// o primeiro quadro ficar pronto, ja sem fundo, para nao dar um salto na troca.
export function montar(container) {
  const v = obterVideo()
  exibindo = true
  v.volume = 1
  v.muted = !querSom

  const poster = document.createElement('img')
  poster.className = 'hero-video'
  poster.src = tema.recursos.videoPoster
  poster.alt = tema.recursos.videoDescricao

  const canvas = document.createElement('canvas')
  canvas.className = 'hero-video'
  canvas.style.display = 'none'
  canvas.setAttribute('role', 'img')
  canvas.setAttribute('aria-label', tema.recursos.videoDescricao)

  const parar = desenharSemFundo(v, canvas, () => {
    canvas.style.display = ''
    poster.remove()
  })

  container.append(poster, canvas, v)
  v.currentTime = 0
  tocar()
  avisar()
  return () => {
    exibindo = false
    parar()
    v.pause()
    v.remove()
    canvas.remove()
    poster.remove()
  }
}

// Ligar o som recomeca do inicio, para a fala nao entrar pela metade. Vale por
// uma passada, como a primeira; desligar continua de onde esta.
export function alternarSom() {
  if (falhou) {
    if (obterAudio().paused) tocarAudio()
    else audio.pause()
    return
  }
  if (!video) return
  video.muted = !video.muted
  if (!video.muted) video.currentTime = 0
  if (video.paused) tocar()
}

// Imagem animada no lugar do video: o som vem do audio de reserva, com a mesma
// regra da primeira passada. Devolve a funcao que para.
export function montarReserva() {
  exibindoReserva = true
  if (querSom) tocarAudio()
  avisar()
  return () => {
    exibindoReserva = false
    if (audio) audio.pause()
  }
}

// Onde a fala esta agora: no video, ou no audio quando a imagem animada substitui
export function tempoAtual() {
  const midia = falhou ? audio : video
  return midia ? midia.currentTime : 0
}

export function ouvir(fn) {
  ouvintes.add(fn)
  return () => ouvintes.delete(fn)
}

export function estaComFalha() {
  return falhou
}
