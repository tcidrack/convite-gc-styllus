import { tema } from "./configuracaoTema"
import { INICIO_PARTES, TRECHOS } from "./partesVideo"

// Segundo `t` do arquivo original da parte -> segundo do video final. Cada
// trecho [oi, of, ni, nf] diz que [oi, of] do original virou [ni, nf] na parte
// montada: corte (ni == nf) ou fala trocada e esticada.
export function tempoNoVideo(parte, t) {
  const inicio = INICIO_PARTES[parte] ?? 0
  let desloc = 0
  for (const [oi, of, ni, nf] of TRECHOS[parte] || []) {
    if (t >= of) desloc = nf - of
    else if (t > oi) return inicio + ni + ((t - oi) * (nf - ni)) / (of - oi)
    else break
  }
  return inicio + t + desloc
}

// As legendas do tema, com inicio e fim no tempo do video final
export const LEGENDAS = (tema.recursos.legendas || [])
  .filter((l) => l.parte in INICIO_PARTES)
  .map((l) => ({
    texto: l.texto,
    inicio: tempoNoVideo(l.parte, l.inicio),
    fim: tempoNoVideo(l.parte, l.fim),
  }))
