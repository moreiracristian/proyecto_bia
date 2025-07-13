// frontend/src/components/Home.jsx
import React from "react";
import { Link } from "react-router-dom";

export default function Home() {
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        minHeight: "100vh",
        textAlign: "center",
        padding: "1rem"
      }}
    >
      <h2>Bienvenido al Sistema BIA</h2>
      <p>Desde aquí podés generar tu certificado libre de deuda:</p>
      <Link
        to="/certificado"
        style={{
          marginTop: "1rem",
          padding: "0.5rem 1rem",
          textDecoration: "none",
          border: "1px solid #007bff",
          borderRadius: "4px",
          color: "#007bff"
        }}
      >
        Generar Certificado
      </Link>
    </div>
  );
}