// frontend/src/services/api.js
import axios from 'axios';

// Instancia Axios para API REST con JWT
const api = axios.create({
  baseURL: '/', 
});

// Carga token al inicializar si existe
const token = localStorage.getItem('access_token');
if (token) {
  api.defaults.headers['Authorization'] = `Bearer ${token}`;
}

export default api;

// Funciones específicas de tu app si lo necesitas
export function fetchCertificados() {
  return api.get('/api/certificados/');
}

export function subirExcel(formData) {
  return api.post('/carga-datos/api/', formData);
}

export function confirmarCarga() {
  return api.post('/carga-datos/api/confirmar/');
}

export function fetchErrores() {
  return api.get('/carga-datos/api/errores/');
}
