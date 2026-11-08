import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

// Enquanto o .env nao estiver preenchido, o cliente fica nulo e as
// confirmacoes caem no fallback de localStorage em vez de quebrar a pagina.
export const supabase =
  supabaseUrl && supabaseAnonKey ? createClient(supabaseUrl, supabaseAnonKey) : null

export const supabaseConfigurado = Boolean(supabase)
