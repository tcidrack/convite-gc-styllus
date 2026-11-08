import { tema, criarUrlCalendario } from "../configuracaoTema"
import { IconeAgenda, IconePin, IconeRota } from "../componentes/Icones"
import { ICONES } from "../componentes/iconesPorNome"
import Cenario from "../componentes/Cenario"
import Logo from "../componentes/Logo"
import Novidades from "../componentes/Novidades"
import VideoBonequinha from "../componentes/VideoBonequinha"

const urlMaps = tema.calendario.mapsUrl
const urlCalendario = criarUrlCalendario(tema)

// Dia da semana tirado da propria data do evento, para nao ter mais um
// campo para lembrar de atualizar quando a data mudar.
function diaDaSemana(dataBR) {
  const [, data] = (dataBR || "").split(" ")
  if (!data) return ""
  const [dia, mes, ano] = data.split("/").map(Number)
  const nome = new Date(ano, mes - 1, dia).toLocaleDateString("pt-BR", { weekday: "long" })
  return nome.split("-")[0].replace(/^./, (c) => c.toUpperCase())
}

const semana = diaDaSemana(tema.calendario.dataInicio)
const { dia, mes, hora, minuto } = tema.dataEvento
const horario = `${hora}h${minuto !== "00" ? minuto : ""}`

// Convite aberto: nao pede confirmacao. A primeira tela leva ate o endereco, com
// o mapa a um toque; o resto do que vai ter fica logo abaixo.
export default function Invite() {
  return (
    <div className="pagina-convite">
      <div className="convite-card">
        <Cenario />

        <VideoBonequinha />

        <div className="convite-conteudo">
          <header className="cabecalho">
            <h1>
              <Logo className="logo-rosa logo-compacta" />
            </h1>
            <p className="evento">{tema.tituloEvento}</p>
            <p className="quando">
              {semana}, {dia} de {mes.toLowerCase()} · a partir das {horario}
            </p>
          </header>

          <ul className="destaques">
            {tema.destaques.map((d) => {
              if (d.valor) {
                return (
                  <li key={d.valor} className="destaque destaque-principal">
                    <strong className="destaque-valor">
                      {d.valor} <small>{d.sufixo}</small>
                    </strong>
                    <span className="destaque-detalhe">{d.detalhe}</span>
                    <span className="destaque-periodo">{d.periodo}</span>
                  </li>
                )
              }
              const Icone = ICONES[d.icone]
              return (
                <li key={d.titulo} className="destaque">
                  <span className="destaque-icone">
                    <Icone />
                  </span>
                  <strong>{d.titulo}</strong>
                  <span className="destaque-detalhe">{d.detalhe}</span>
                </li>
              )
            })}
          </ul>

          <section className="endereco" aria-label="Endereço">
            <p className="endereco-rotulo">
              <IconePin />
              {tema.local.titulo}
            </p>
            <p className="endereco-rua">{tema.local.rua}</p>
            <p className="endereco-bairro">{tema.local.bairro}</p>
            <div className="endereco-acoes">
              <a href={urlMaps} target="_blank" rel="noreferrer" className="botao-mapa">
                <IconeRota />
                <span>{tema.local.botaoMapa}</span>
              </a>
              <a href={urlCalendario} target="_blank" rel="noreferrer" className="botao-agenda">
                <IconeAgenda />
                <span>{tema.local.botaoAgenda}</span>
              </a>
            </div>
          </section>

          <section className="mais">
            <h2 className="mais-titulo">{tema.novidades.titulo}</h2>
            <Novidades />
          </section>

          <p className="assinatura">
            {tema.assinatura.texto} {tema.assinatura.nome} ·{" "}
            <a href={tema.assinatura.url} target="_blank" rel="noreferrer">
              {tema.assinatura.instagram}
            </a>
          </p>
        </div>
      </div>
    </div>
  )
}
