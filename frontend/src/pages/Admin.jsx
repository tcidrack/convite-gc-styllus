import { useCallback, useEffect, useState } from "react"
import { supabase } from "../services/supabase"
import { tema } from "../configuracaoTema"
import Cenario from "../componentes/Cenario"

// A lista so sai do banco pela funcao listar_confirmados_gc_styllus, que confere
// a senha la dentro (database.sql, bloco 6). A tabela nao tem leitura publica:
// a chave anon vai no site, entao qualquer convidado conseguiria listar todos.
const FUNCAO = tema.funcaoListar
// Guarda a senha so ate fechar a aba, para a lista se atualizar sozinha
const CHAVE_SENHA = "senha_admin_gc_styllus"

function formatarHorario(iso) {
  if (!iso) return ""
  return new Date(iso).toLocaleString("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  })
}

function lerSenhaSalva() {
  try {
    return sessionStorage.getItem(CHAVE_SENHA) || ""
  } catch {
    return ""
  }
}

function salvarSenha(senha) {
  try {
    if (senha) sessionStorage.setItem(CHAVE_SENHA, senha)
    else sessionStorage.removeItem(CHAVE_SENHA)
  } catch {
    // aba anonima sem storage: so nao lembra a senha
  }
}

export default function Admin() {
  const [senha, setSenha] = useState(lerSenhaSalva)
  const [digitada, setDigitada] = useState("")
  const [confirmados, setConfirmados] = useState(null) // null = ainda nao entrou
  const [carregando, setCarregando] = useState(false)
  const [erro, setErro] = useState(null)

  // So mexe no estado depois da resposta do banco: o "carregando" e ligado
  // no clique de entrar, nao aqui (este callback tambem roda dentro do efeito).
  const carregar = useCallback(async (senhaUsada) => {
    if (!supabase) return
    try {
      const { data, error } = await supabase.rpc(FUNCAO, { p_senha: senhaUsada })
      if (error) {
        if ((error.message || "").includes("SENHA_INVALIDA")) {
          salvarSenha("")
          setSenha("")
          setConfirmados(null)
          setErro("Senha incorreta")
        } else {
          console.error("Erro ao carregar confirmados:", error)
          setErro(
            error.code === "PGRST202"
              ? "A função ainda não existe no Supabase — rode o database.sql (bloco 6)."
              : "Erro: " + error.message
          )
        }
        return
      }
      setErro(null)
      salvarSenha(senhaUsada)
      setConfirmados(data || [])
    } catch (e) {
      console.error("Erro ao carregar dados:", e)
      setErro("Erro inesperado ao carregar lista")
    } finally {
      setCarregando(false)
    }
  }, [])

  // Busca ao entrar e a cada 30s. A primeira vai num setTimeout 0 so para
  // sair do corpo do efeito (regra react-hooks/set-state-in-effect).
  useEffect(() => {
    if (!senha) return
    const primeira = setTimeout(() => carregar(senha), 0)
    const intervalo = setInterval(() => carregar(senha), 30000)
    return () => {
      clearTimeout(primeira)
      clearInterval(intervalo)
    }
  }, [senha, carregar])

  function entrar(e) {
    e.preventDefault()
    if (!digitada) return
    setErro(null)
    setCarregando(true)
    setSenha(digitada)
    setDigitada("")
  }

  function sair() {
    salvarSenha("")
    setSenha("")
    setConfirmados(null)
    setErro(null)
  }

  const logado = Boolean(senha) && confirmados !== null

  return (
    <div className="admin-page">
      <Cenario />

      <div className="admin-card">
        <h1>Convidados confirmados</h1>
        <p className="admin-sub">{tema.calendario.eventoNome}</p>

        {!supabase && (
          <p className="admin-erro">Supabase não configurado — preencha o arquivo .env</p>
        )}
        {erro && <p className="admin-erro">{erro}</p>}

        {!logado && (
          <form className="admin-login" onSubmit={entrar}>
            <input
              type="password"
              placeholder="Senha"
              value={digitada}
              onChange={(e) => setDigitada(e.target.value)}
              autoFocus
            />
            <button type="submit" disabled={carregando || !digitada}>
              {carregando ? "Entrando..." : "Ver lista"}
            </button>
          </form>
        )}

        {logado && (
          <>
            <div className="admin-total">
              <span className="admin-total-num">{confirmados.length}</span>
              <span className="admin-total-texto">
                {confirmados.length === 1 ? "confirmação" : "confirmações"}
              </span>
            </div>

            {confirmados.length === 0 && (
              <p className="admin-vazio">Nenhum convidado confirmado ainda.</p>
            )}

            <ol className="admin-lista">
              {confirmados.map((c, i) => (
                <li key={c.id}>
                  <span className="admin-pos">{i + 1}</span>
                  <span className="admin-nome">{c.nome}</span>
                  <span className="admin-hora">{formatarHorario(c.created_at)}</span>
                </li>
              ))}
            </ol>

            <button type="button" className="admin-sair" onClick={sair}>
              Sair
            </button>
          </>
        )}
      </div>
    </div>
  )
}
