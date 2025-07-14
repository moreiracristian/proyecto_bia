// frontend/src/components/ErroresValidacion.jsx
import React, { useState, useEffect } from 'react';
import { fetchErrores } from '../services/api';

export default function ErroresValidacion() {
  const [errors, setErrors] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    (async () => {
      try {
        const res = await fetchErrores();
        if (res.data.success) {
          setErrors(res.data.errors);
        } else {
          setError(res.data.error);
        }
      } catch (err) {
        setError('Error al obtener errores.');
      }
    })();
  }, []);

  return (
    <div style={{ padding: '1rem' }}>
      <h2>Errores de Validación</h2>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {errors.length > 0 ? (
        <ul>
          {errors.map((errMsg, i) => (
            <li key={i}>{errMsg}</li>
          ))}
        </ul>
      ) : (
        !error && <p>No hay errores.</p>
      )}
      {errors.length > 0 && (
        <a
          href="/carga-datos/api/errores/?exportar=txt"
          style={{ display: 'inline-block', marginTop: '1rem' }}
        >
          Descargar errores
        </a>
      )}
    </div>
  );
}
