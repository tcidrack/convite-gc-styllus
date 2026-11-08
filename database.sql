-- ============================================================
--  Convite da Inauguração da GC STYLLUS
--  Schema completo — SQL Editor do Supabase
-- ============================================================
--
--  O script inteiro é idempotente: pode ser executado de novo
--  quantas vezes for preciso, sem dar erro.
--
--  Roda no MESMO projeto Supabase dos outros convites. Por isso
--  tudo aqui tem nome próprio (sufixo gc_styllus): reusar um nome
--  sobrescreveria a função ou a senha de outro convite.
-- ============================================================


-- ── 1. Confirmações ───────────────────────────────────────────

CREATE TABLE IF NOT EXISTS public.confirmacoes_inauguracao_gc_styllus (
  id         BIGINT GENERATED ALWAYS AS IDENTITY NOT NULL,
  nome       TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  CONSTRAINT confirmacoes_inauguracao_gc_styllus_pkey PRIMARY KEY (id)
) TABLESPACE pg_default;


-- ── 2. Confirmar presença ─────────────────────────────────────
-- Toda confirmação passa por aqui: valida o nome e barra nome
-- repetido (sem diferenciar maiúsculas).

CREATE OR REPLACE FUNCTION public.confirmar_presenca_gc_styllus(p_nome TEXT)
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_nome TEXT := btrim(coalesce(p_nome, ''));
BEGIN
  IF v_nome = '' THEN
    RAISE EXCEPTION 'NOME_VAZIO';
  END IF;

  IF length(v_nome) > 120 THEN
    v_nome := left(v_nome, 120);
  END IF;

  IF EXISTS (
    SELECT 1 FROM public.confirmacoes_inauguracao_gc_styllus c
     WHERE lower(c.nome) = lower(v_nome)
  ) THEN
    RAISE EXCEPTION 'NOME_DUPLICADO';
  END IF;

  INSERT INTO public.confirmacoes_inauguracao_gc_styllus (nome)
  VALUES (v_nome);
END;
$$;


-- ── 3. RLS e permissões ───────────────────────────────────────

ALTER TABLE public.confirmacoes_inauguracao_gc_styllus ENABLE ROW LEVEL SECURITY;

-- Leitura FECHADA de propósito. A chave anon vai dentro do site, então uma
-- policy de select liberada deixava qualquer convidado listar o nome de todos.
-- A /admin lê pela função listar_confirmados_gc_styllus (bloco 6), que pede senha.
-- Sem policy de insert de propósito: inserir só pela função acima.

GRANT EXECUTE ON FUNCTION public.confirmar_presenca_gc_styllus(TEXT) TO anon;


-- ── 4. Conferir o estado ──────────────────────────────────────
--
-- SELECT nome, created_at
--   FROM public.confirmacoes_inauguracao_gc_styllus ORDER BY created_at;


-- ── 5. Limpeza de teste ───────────────────────────────────────
--
-- DELETE FROM public.confirmacoes_inauguracao_gc_styllus WHERE nome ILIKE 'TESTE%';


-- ── 6. Senha da /admin e leitura da lista ─────────────────────
--
--     >>> TROQUE 'TROQUE_ESTA_SENHA' PELA SENHA QUE VOCÊ QUER <<<
--
-- Guarda só o hash (bcrypt). A tabela tem RLS ligada e NENHUMA policy, então
-- a chave anon não lê nada dela — só a função abaixo enxerga.
-- Rodar de novo com outro valor troca a senha.

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA extensions;

CREATE TABLE IF NOT EXISTS public.config_admin_gc_styllus (
  id         INTEGER PRIMARY KEY DEFAULT 1,
  senha_hash TEXT NOT NULL,
  CONSTRAINT config_admin_gc_styllus_linha_unica CHECK (id = 1)
);

ALTER TABLE public.config_admin_gc_styllus ENABLE ROW LEVEL SECURITY;

INSERT INTO public.config_admin_gc_styllus (id, senha_hash)
VALUES (1, extensions.crypt('TROQUE_ESTA_SENHA', extensions.gen_salt('bf')))
ON CONFLICT (id) DO UPDATE
  SET senha_hash = EXCLUDED.senha_hash;

-- A senha é conferida aqui dentro, no banco: conferir no JavaScript não
-- adiantaria nada, já que o código roda no navegador de quem abre o site.
CREATE OR REPLACE FUNCTION public.listar_confirmados_gc_styllus(p_senha TEXT)
RETURNS TABLE (id BIGINT, nome TEXT, created_at TIMESTAMP WITH TIME ZONE)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, extensions
AS $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM public.config_admin_gc_styllus ca
     WHERE ca.senha_hash = extensions.crypt(coalesce(p_senha, ''), ca.senha_hash)
  ) THEN
    RAISE EXCEPTION 'SENHA_INVALIDA';
  END IF;

  RETURN QUERY
  SELECT c.id, c.nome, c.created_at
    FROM public.confirmacoes_inauguracao_gc_styllus c
   ORDER BY c.created_at;
END;
$$;

GRANT EXECUTE ON FUNCTION public.listar_confirmados_gc_styllus(TEXT) TO anon;

-- Conferir que ninguém lê a tabela direto (deve voltar VAZIO):
--
-- SELECT policyname, cmd FROM pg_policies
--  WHERE tablename IN ('confirmacoes_inauguracao_gc_styllus', 'config_admin_gc_styllus');
