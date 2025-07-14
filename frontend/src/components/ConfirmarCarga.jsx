// frontend/src/components/ConfirmarCarga.jsx
import React, { useState, useEffect } from 'react';
import { confirmarCarga } from '../services/api';
import { useNavigate } from 'react-router-dom';

export default function ConfirmarCarga() {
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    (async () => {
      try {
        const res = await confirmarCarga();
        if (res.data.success) {
          setMessage(`✅ Se crearon ${res.data.created_count} registros.`);
          // Redirige después de 2 segundos
          setTimeout(() => navigate('/carga-datos/errores'), 2000);
        } else {
          setError(res.data.error);
        }
      } catch (err) {
        setError('Error al confirmar la carga.');
      }
    })();
  }, [navigate]);

  return (
    <div style={{ padding: '1rem' }}>
      <h2>Confirmar Carga</h2>
      {message && <p style={{ color: 'green' }}>{message}</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
}