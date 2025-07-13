// frontend/src/App.js
import React from "react";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import GenerarCertificado from "./components/GenerarCertificado";
// import Home or cualquier otro componente que tengas
import Home from "./components/Home";

function App() {
  return (
    <BrowserRouter>
      <nav>
        <Link to="/">Home</Link> |{" "}
        <Link to="/certificado">Generar Certificado</Link>
      </nav>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/certificado" element={<GenerarCertificado />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;

