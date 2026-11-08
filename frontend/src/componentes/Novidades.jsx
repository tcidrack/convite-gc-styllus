import { useEffect, useState } from "react"
import { tema } from "../configuracaoTema"
import { ICONES } from "./iconesPorNome"

const { itens, intervalo } = tema.novidades

// Uma novidade por vez, trocando sozinha, como as fotos do convite da Thayla.
// Todas ficam empilhadas na mesma celula da grade: assim a janela sempre tem a
// altura da maior e nao pula a cada troca.
export default function Novidades() {
  const [atual, setAtual] = useState(0)
  const [automatico, setAutomatico] = useState(true)

  useEffect(() => {
    if (!automatico) return
    const timer = setTimeout(() => setAtual((a) => (a + 1) % itens.length), intervalo)
    return () => clearTimeout(timer)
  }, [atual, automatico])

  function escolher(i) {
    setAutomatico(false)
    setAtual(i)
  }

  return (
    <div className="novidades">
      <div className="novidades-palco">
        {itens.map((item, i) => {
          const Icone = ICONES[item.icone]
          return (
            <div key={item.titulo} className={`novidade ${i === atual ? "ativa" : ""}`} aria-hidden={i !== atual}>
              <span className="novidade-icone">
                <Icone />
              </span>
              <h3>{item.titulo}</h3>
              {item.texto && <p>{item.texto}</p>}
              {item.lista && (
                <ul className="novidade-lista">
                  {item.lista.map((nome) => (
                    <li key={nome}>{nome}</li>
                  ))}
                </ul>
              )}
              {item.fim && <p className="novidade-fim">{item.fim}</p>}
            </div>
          )
        })}
      </div>

      <div className="novidades-pontos">
        {itens.map((item, i) => (
          <button
            key={item.titulo}
            type="button"
            className={i === atual ? "ativo" : ""}
            onClick={() => escolher(i)}
            aria-label={`Ver: ${item.titulo}`}
            aria-current={i === atual}
          />
        ))}
      </div>
    </div>
  )
}
