// frontend/src/components/ListaCertificados.jsx
import { useState, useEffect } from "react";
import axios from "axios";

export default function ListaCertificados() {
  const [certificados, setCertificados] = useState([]);

  useEffect(() => {
    axios.get("/api/certificados/")
      .then(res => setCertificados(res.data))
      .catch(err => console.error(err));
  }, []);

  return (
    <ul>
      {certificados.map(c => (
        <li key={c.id}>{c.nombre}</li>
      ))}
    </ul>
  );
}
