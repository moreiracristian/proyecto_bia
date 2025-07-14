// frontend/src/services/auth.js
import api from './api';

/**
 * Inicia sesión usando JWT en lugar de sesiones de Django.
 * Envía credenciales y guarda los tokens en localStorage.
 */
export async function login(username, password) {
  const response = await api.post('/api/token/', { username, password });
  const { access, refresh } = response.data;
  localStorage.setItem('access_token', access);
  localStorage.setItem('refresh_token', refresh);
  // Adjunta el token a futuros requests de api
  api.defaults.headers['Authorization'] = `Bearer ${access}`;
}

/**
 * Borra los tokens y el header de autorización.
 */
export function logout() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  delete api.defaults.headers['Authorization'];
}

/**
 * Comprueba si hay un token de acceso activo.
 */
export function isLoggedIn() {
  return !!localStorage.getItem('access_token');
}

/**
 * Refresca el token de acceso usando el refresh token.
 */
export async function refreshToken() {
  const refresh = localStorage.getItem('refresh_token');
  if (!refresh) throw new Error('No refresh token available');
  const response = await api.post('/api/token/refresh/', { refresh });
  const { access } = response.data;
  localStorage.setItem('access_token', access);
  api.defaults.headers['Authorization'] = `Bearer ${access}`;
  return access;
}
