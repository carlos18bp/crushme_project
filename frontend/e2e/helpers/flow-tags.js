/**
 * Flow tag constants for consistent E2E test tagging.
 *
 * Usage:
 *   import { AUTH_LOGIN } from '../helpers/flow-tags.js';
 *   test('...', { tag: [...AUTH_LOGIN, '@role:shared'] }, async ({ page }) => { ... });
 */

// ── Auth ──
export const AUTH_LOGIN = ['@flow:auth-login', '@module:auth', '@priority:P1'];
export const AUTH_REGISTER = ['@flow:auth-register', '@module:auth', '@priority:P1'];

// ── Public ──
export const PUBLIC_HOME = ['@flow:public-home', '@module:public', '@priority:P2'];
