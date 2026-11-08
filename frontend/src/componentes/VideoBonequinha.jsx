import { useEffect, useRef, useState } from "react"
import { tema } from "../configuracaoTema"
import { alternarSom, estaComFalha, montar, montarReserva, ouvir } from "../services/videoBonequinha"
import Cenario from "./Cenario"
import { IconeSom } from "./Icones"
import Legenda from "./Legenda"

export default function VideoBonequinha() {
  const lugarRef = useRef(null)
  const [estado, setEstado] = useState(() => ({ falhou: estaComFalha(), mudo: true }))

  useEffect(() => ouvir(setEstado), [])

  // O elemento <video> vem do servico, ja liberado pelo toque no envelope
  useEffect(() => {
    if (estado.falhou || !lugarRef.current) return
    return montar(lugarRef.current)
  }, [estado.falhou])

  useEffect(() => {
    if (estado.falhou) return montarReserva()
  }, [estado.falhou])

  return (
    <div className="hero">
      <Cenario />
      {estado.falhou ? (
        <img className="hero-video" src={tema.recursos.videoAnimado} alt={tema.recursos.videoDescricao} />
      ) : (
        <div className="hero-lugar" ref={lugarRef} />
      )}
      <Legenda />
      <button
        type="button"
        className={`botao-som ${estado.mudo ? "botao-som-chamada" : ""}`}
        onClick={alternarSom}
        aria-label={estado.mudo ? "Ouvir o vídeo de novo, com som" : "Desligar o som do vídeo"}
      >
        <IconeSom mudo={estado.mudo} />
        {estado.mudo && <span>Ouvir de novo</span>}
      </button>
    </div>
  )
}
