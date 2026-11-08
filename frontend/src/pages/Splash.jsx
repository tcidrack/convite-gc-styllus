import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { tema } from "../configuracaoTema"
import Cenario from "../componentes/Cenario"
import Logo from "../componentes/Logo"
import { liberarSom, preCarregar } from "../services/videoBonequinha"

export default function Splash() {
  const navigate = useNavigate()
  const [aberto, setAberto] = useState(false)

  // Comeca a baixar o video antes do toque, para o convite abrir ja com ele
  useEffect(() => preCarregar(), [])

  function abrirEnvelope() {
    if (aberto) return
    setAberto(true)
    // Tem que ser aqui, dentro do toque: navegador nao deixa ligar som sozinho
    liberarSom()
    setTimeout(() => {
      navigate("/convite")
    }, 1600)
  }

  return (
    <div className="splash-container">
      <Cenario />

      <p className="splash-titulo">{tema.envelope.convite}</p>

      <button
        type="button"
        className={`envelope ${aberto ? "aberto" : ""}`}
        onClick={abrirEnvelope}
        aria-label={tema.envelope.clique}
      >
        <span className="envelope-corpo" />
        <span className="envelope-cartao">
          <Logo className="logo-rosa" />
        </span>
        <span className="envelope-lado-esq" />
        <span className="envelope-lado-dir" />
        <span className="envelope-aba" />
        <span className="selo">
          <span className="selo-inicial">{tema.iniciais}</span>
        </span>
      </button>

      <p className="splash-texto">{aberto ? tema.envelope.abrindo : tema.envelope.clique}</p>
    </div>
  )
}
