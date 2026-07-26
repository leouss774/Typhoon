/**
 * Supabase Auth Service — Magic Link & OAuth
 * ==========================================
 * Bridges Supabase Auth (magic link, Google OAuth) with the
 * backend session cookie flow.
 *
 * Flow:
 *   1. User clicks "Magic Link" → supabase.auth.signInWithOtp({ email })
 *   2. User receives email, clicks link, gets redirected back
 *   3. Page detects Supabase session in URL hash
 *   4. Sends Supabase access token to POST /api/auth/supabase-login
 *   5. Backend verifies the JWT, creates local user if needed, sets cookie
 *   6. Frontend navigates to dashboard
 */

import { supabase } from './client'
import { apiFetch } from '../../api/client'

/**
 * Send a magic link email to the user.
 * Supabase handles the email delivery; the user clicks the link
 * and gets redirected back to the app with a session.
 */
export async function sendMagicLink(email: string): Promise<void> {
  const { error } = await supabase.auth.signInWithOtp({
    email,
    options: {
      // After clicking the magic link, redirect back here.
      // The emailRedirectTo should point to the app's current URL.
      emailRedirectTo: window.location.origin,
    },
  })

  if (error) {
    throw new Error(error.message || 'Échec de l\'envoi du lien magique')
  }
}

/**
 * Exchange a Supabase OAuth access token with the backend.
 * The backend verifies the JWT, creates a local user if needed,
 * and sets an httpOnly cookie for session continuity.
 */
export async function exchangeSupabaseSession(): Promise<{ id: string; email: string; firstName: string; lastName: string; role: string } | null> {
  // Get current Supabase session
  const { data: { session } } = await supabase.auth.getSession()

  if (!session?.access_token) {
    return null
  }

  // Send the access token to the backend
  const data = await apiFetch<{ user: { id: string; email: string; first_name: string; last_name: string; role: string } }>(
    '/api/auth/supabase-login',
    {
      method: 'POST',
      body: JSON.stringify({ access_token: session.access_token }),
    },
  )

  return {
    id: data.user.id,
    email: data.user.email,
    firstName: data.user.first_name,
    lastName: data.user.last_name,
    role: data.user.role,
  }
}

/**
 * Detect if the current page load is a Supabase Auth callback
 * (magic link or OAuth redirect). If so, handle the session
 * and return true.
 */
export async function handleAuthCallback(): Promise<boolean> {
  // Check if URL hash contains Supabase session fragments
  const hash = window.location.hash
  if (hash && (hash.includes('access_token') || hash.includes('type=signup') || hash.includes('type=recovery'))) {
    // Let Supabase process the hash (it stores the session internally)
    const { data, error } = await supabase.auth.getSession()
    if (error || !data.session) {
      // Try to let Supabase handle the hash
      await supabase.auth.setSession({
        access_token: '',
        refresh_token: '',
      })
      return false
    }

    // Exchange the Supabase session for a backend cookie
    const user = await exchangeSupabaseSession()
    if (user) {
      // Clear the hash from URL
      window.history.replaceState(null, '', window.location.pathname)
      return true
    }
  }

  // Also check if there's already a persistent Supabase session
  const { data: { session } } = await supabase.auth.getSession()
  if (session?.access_token) {
    // Check if we have a backend cookie too by trying /me
    try {
      await apiFetch('/api/auth/me')
      // Cookie exists — session is valid
      return true
    } catch {
      // No backend cookie — exchange the Supabase session
      const user = await exchangeSupabaseSession()
      return !!user
    }
  }

  return false
}

/**
 * Sign out from Supabase and clear the local cookie.
 */
export async function supabaseSignOut(): Promise<void> {
  await supabase.auth.signOut()
}
