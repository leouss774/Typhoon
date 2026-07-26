/**
 * Auth middleware — reads JWT from httpOnly cookie and injects user into context.
 */
import type { Context, Next } from 'hono';
import { verifyToken } from '../../services/auth.service.js';
import type { JwtPayload } from '../../services/auth.service.js';

export type AuthEnv = {
  Variables: {
    user: JwtPayload;
  };
};

// Lazy-initialized dev user cache
let devUserCache: { sub: string; email: string; role: string } | null = null;

async function getDevUser(): Promise<{ sub: string; email: string; role: string }> {
  if (devUserCache) return devUserCache;
  try {
    const { db } = await import('../../database/client.js');
    const { users } = await import('../../database/schema.js');
    const firstUser = await db.select().from(users).limit(1).get();
    if (firstUser) {
      devUserCache = { sub: firstUser.id, email: firstUser.email, role: firstUser.role };
      return devUserCache;
    }
  } catch {}
  return { sub: 'dev-user-id', email: 'dev@previa.fr', role: 'assureur' };
}

export async function requireAuth(c: Context, next: Next): Promise<Response | void> {
  // Dev bypass: when AUTH_DISABLED=true, inject first DB user
  if (process.env.AUTH_DISABLED === 'true') {
    c.set('user', await getDevUser());
    await next();
    return;
  }

  const cookie = c.req.header('cookie') ?? '';
  const token = parseCookie(cookie, 'token');

  if (!token) {
    return c.json({ error: 'UNAUTHORIZED', message: 'Authentication required' }, 401);
  }

  const payload = await verifyToken(token);
  if (!payload) {
    return c.json({ error: 'UNAUTHORIZED', message: 'Invalid or expired session' }, 401);
  }

  c.set('user', payload);
  await next();
}

export async function optionalAuth(c: Context, next: Next): Promise<void> {
  const cookie = c.req.header('cookie') ?? '';
  const token = parseCookie(cookie, 'token');
  if (token) {
    const payload = await verifyToken(token);
    if (payload) c.set('user', payload);
  }
  await next();
}

function parseCookie(cookieHeader: string, name: string): string | null {
  const match = cookieHeader.match(new RegExp(`(?:^|;\\s*)${name}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : null;
}
