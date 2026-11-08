import { useState } from "react"
import { supabase } from "../services/supabase"
import { tema, criarUrlCalendario } from "../configuracaoTema"
import { IconePin, IconeCheck } from "../componentes/Icones"
import { ICONES } from "../componentes/iconesPorNome"
import Cenario from "../componentes/Cenario"
import Logo from "../componentes/Logo"
import Novidades from "../componentes/Novidades"
import VideoBonequinha from "../componentes/VideoBonequinha"

const urlMaps = tema.calendario.mapsUrl
const urlCalendario = criarUrlCalendario(tema)
const CHAVE_LOCAL = "confirmado_inauguracao_gc_styllus"
const CHAVE_LISTA = "confirmacoes_gc_styllus"

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

// Mensagens das exceções levantadas pela função de confirmação no banco.
const ERROS = {
  NOME_VAZIO: ["error", "Digite seu nome 💖"],
  NOME_DUPLICADO: ["error", "Já há confirmação para este nome"],
}

function lerErro(mensagem) {
  const chave = Object.keys(ERROS).find((k) => (mensagem || "").includes(k))
  return chave ? ERROS[chave] : null
}

export default function Invite() {
  const [nome, setNome] = useState("")
  const [mostrarConfirmacao, setMostrarConfirmacao] = useState(false)
  const [confirmando, setConfirmando] = useState(false)
  const [mostrarObrigado, setMostrarObrigado] = useState(false)
  const [toast, setToast] = useState(null)
  const [jaConfirmado, setJaConfirmado] = useState(
    () => localStorage.getItem(CHAVE_LOCAL) !== null
  )

  function salvarLocalmente(nomeConfirmado) {
    try {
      const listaAtual = JSON.parse(localStorage.getItem(CHAVE_LISTA) || "[]")
      const atualizado = [
        ...listaAtual,
        { id: Date.now(), nome: nomeConfirmado, createdAt: new Date().toISOString() },
      ]
      localStorage.setItem(CHAVE_LISTA, JSON.stringify(atualizado))
    } catch (err) {
      console.error("Erro ao salvar localmente:", err)
    }
  }

  function showToast(type, text, ms = 3000) {
    setToast({ type, text })
    setTimeout(() => setToast(null), ms)
  }

  function finalizarConfirmacao(nomeConfirmado) {
    localStorage.setItem(CHAVE_LOCAL, nomeConfirmado)
    setJaConfirmado(true)
    setNome("")
    setMostrarConfirmacao(false)
    // Em vez de abrir a agenda sozinho (o navegador bloqueia window.open depois
    // de um await), abre a janela de agradecimento com o botao da agenda.
    setMostrarObrigado(true)
  }

  async function confirmar() {
    const nomeTrim = nome.trim()
    if (!nomeTrim) {
      showToast("error", "Digite seu nome 💖")
      return
    }

    setConfirmando(true)
    try {
      if (!supabase) {
        salvarLocalmente(nomeTrim)
        finalizarConfirmacao(nomeTrim)
        return
      }

      const { error } = await supabase.rpc(tema.funcaoConfirmar, { p_nome: nomeTrim })

      if (error) {
        const conhecido = lerErro(error.message)
        if (conhecido) {
          showToast(...conhecido)
          return
        }
        console.error("Erro ao confirmar presença:", error)
        salvarLocalmente(nomeTrim)
        showToast("info", "Não foi possível salvar no servidor — salvo localmente 👍")
        setNome("")
        setMostrarConfirmacao(false)
        return
      }

      finalizarConfirmacao(nomeTrim)
    } catch (error) {
      console.error("Erro ao confirmar presença:", error)
      salvarLocalmente(nomeTrim)
      showToast("info", "Erro inesperado — salvo localmente")
      setNome("")
      setMostrarConfirmacao(false)
    } finally {
      setConfirmando(false)
    }
  }

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

          <a href={urlMaps} target="_blank" rel="noreferrer" className="local">
            <IconePin />
            <span>{tema.calendario.endereco}</span>
          </a>

          {jaConfirmado ? (
            <button type="button" className="acao-confirmar confirmado" onClick={() => setMostrarObrigado(true)}>
              <IconeCheck preenchido />
              <span>Presença confirmada</span>
            </button>
          ) : (
            <button type="button" className="acao-confirmar" onClick={() => setMostrarConfirmacao(true)}>
              <IconeCheck />
              <span>Confirmar presença</span>
            </button>
          )}

          {jaConfirmado ? (
            <button type="button" className="chamada chamada-link" onClick={() => setMostrarObrigado(true)}>
              {tema.agradecimento.botaoVer}
            </button>
          ) : (
            <p className="chamada">{tema.chamada}</p>
          )}

          <p className="assinatura">
            {tema.assinatura.texto} {tema.assinatura.nome} ·{" "}
            <a href={tema.assinatura.url} target="_blank" rel="noreferrer">
              {tema.assinatura.instagram}
            </a>
          </p>
        </div>
      </div>

      {mostrarConfirmacao && (
        <div className="modal-overlay">
          <div className="modal">
            <button className="close-modal" onClick={() => setMostrarConfirmacao(false)} aria-label="Fechar">
              ✖
            </button>
            <h2>Confirme sua presença</h2>
            <p>Digite seu nome e sobrenome para confirmar sua presença na inauguração.</p>
            <input
              placeholder="Nome e sobrenome"
              aria-label="Nome e sobrenome"
              value={nome}
              onChange={(e) => setNome(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !confirmando && confirmar()}
              autoFocus
            />

            <button className="btn-confirmar" onClick={confirmar} disabled={confirmando}>
              {confirmando ? "Confirmando..." : "Confirmar presença"}
            </button>
          </div>
        </div>
      )}

      {mostrarObrigado && (
        <div className="modal-overlay" onClick={() => setMostrarObrigado(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <button className="close-modal" onClick={() => setMostrarObrigado(false)} aria-label="Fechar">
              ✖
            </button>
            <h2>{tema.agradecimento.titulo}</h2>
            <p>{tema.agradecimento.subtitulo}</p>
            <Novidades />
            <a href={urlCalendario} target="_blank" rel="noreferrer" className="btn-confirmar btn-link">
              {tema.agradecimento.botaoAgenda}
            </a>
            <a href={urlMaps} target="_blank" rel="noreferrer" className="acao-secundaria btn-link">
              {tema.agradecimento.botaoMapa}
            </a>
          </div>
        </div>
      )}

      {toast && <div className={`toast toast-${toast.type}`}>{toast.text}</div>}
    </div>
  )
}
