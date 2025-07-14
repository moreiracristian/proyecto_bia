// frontend/src/components/Logout.jsx
import { useEffect } from 'react';
import { logout } from '../services/auth';

export default function Logout() {
  useEffect(() => {
    // Elimina tokens y encabezados
    logout();
    // Redirige a la página de login o home
    window.location.href = '/login';
  }, []);

  return null; // No renderiza nada
}
