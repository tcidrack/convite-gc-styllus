import { useEffect, useState } from "react"
import { tema } from "../configuracaoTema"
import { tempoAtual } from "../services/videoBonequinha"

const LEGENDAS = tema.recursos.legendas || []

function fraseEm(segundos) {
  const legenda = LEGENDAS.find((l) => segundos >= l.inicio && segundos < l.fim)
  return legenda ? legenda.texto : ""
}

// Acompanha a fala a cada quadro; o React so redesenha quando a frase muda.
// aria-hidden: repete o que o audio ja diz.
export default function Legenda() {
  const [texto, setTexto] = useState("")

  useEffect(() => {
    let quadro
    const acompanhar = () => {
      setTexto(fraseEm(tempoAtual()))
      quadro = requestAnimationFrame(acompanhar)
    }
    quadro = requestAnimationFrame(acompanhar)
    return () => cancelAnimationFrame(quadro)
  }, [])

  if (!texto) return null
  return (
    <p className="legenda" aria-hidden="true">
      {texto}
    </p>
  )
}
