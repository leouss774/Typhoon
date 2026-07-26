/**
 * Supabase Client — Vite/SPA Browser Client
 * =========================================
 * Creates a Supabase client for the browser-based (Vite) frontend.
 *
 * NOTE: The user pasted a Next.js SSR setup guide (server.ts, middleware.ts),
 * but this is a Vite SPA — no server-side rendering or middleware is needed.
 * Only the browser client (this file) is required for a Vite app.
 *
 * Usage:
 *   import { supabase } from '../../utils/supabase/client'
 *   const { data } = await supabase.from('properties').select('*')
 */

import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

export const supabase = createClient(
  supabaseUrl || '',
  supabaseAnonKey || '',
  {
    auth: {
      autoRefreshToken: true,
      persistSession: true,
      detectSessionInUrl: true,
    },
  }
)
