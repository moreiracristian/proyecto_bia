// frontend/src/components/CargaDatos.jsx
import React, { useState } from 'react';
import { subirExcel } from '../services/api';
import { Link } from 'react-router-dom';

export default function CargaDatos() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState('');
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    setError('');
    setPreview('');
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Por favor selecciona un archivo (.csv, .xls, .xlsx).');
      return;
    }
    const formData = new FormData();
    formData.append('archivo', file);
    try {
      const res = await subirExcel(formData);
      if (res.data.success) {
        setPreview(res.data.preview);
      } else {
        setError(res.data.errors.join(', '));
      }
    } catch (err) {
      setError('Error en la carga del archivo.');
    }
  };

  return (
    <div style={{ padding: '1rem' }}>
      <h2>Carga de Datos</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="file"
          accept=".csv,.xls,.xlsx"
          onChange={handleFileChange}
        />
        <button type="submit" style={{ marginTop: '0.5rem' }}>
          Subir
        </button>
      </form>
      {error && <p style={{ color: 'red', marginTop: '1rem' }}>{error}</p>}
      {preview && (
        <div style={{ marginTop: '1rem' }}>
          <h3>Vista Previa</h3>
          <div
            dangerouslySetInnerHTML={{ __html: preview }}
          />
          <Link
            to="/carga-datos/confirmar"
            style={{ display: 'inline-block', marginTop: '1rem', padding: '0.5rem 1rem', border: '1px solid #28a745', borderRadius: 4, color: '#28a745', textDecoration: 'none' }}
          >
            Confirmar Carga
          </Link>
        </div>
      )}
    </div>
  );
}
