// frontend/src/App.js
import React from "react";
import { BrowserRouter, Routes, Route, Link, Navigate, useLocation } from "react-router-dom";
import GenerarCertificado from "./components/GenerarCertificado";
import Home from "./components/Home";
import Login from "./components/Login";
import Logout from "./components/Logout";
import CargaDatos from "./components/CargaDatos";
import ConfirmarCarga from "./components/ConfirmarCarga";
import ErroresValidacion from "./components/ErroresValidacion";
import { isLoggedIn } from "./services/auth";

// Componente para el contenido dentro del Router
function AppContent() {
  const location = useLocation();
  return (
    <>
      <nav style={{ padding: "1rem", textAlign: "center" }}>
        <Link to="/">Home</Link> |{' '}
        <Link to="/certificado">Generar Certificado</Link> |{' '}
        <Link to="/carga-datos">Panel interno</Link>
        {location.pathname.startsWith('/carga-datos') && (
          <>
            {' '}|{' '}
            <Link to="/logout">Cerrar Sesión</Link>
          </>
        )}
      </nav>

      <Routes>
        {/* Rutas públicas */}
        <Route path="/" element={<Home />} />
        <Route path="/certificado" element={<GenerarCertificado />} />
        <Route path="/login" element={<Login />} />

        {/* Rutas internas protegidas */}
        <Route
          path="/carga-datos"
          element={
            <PrivateRoute>
              <CargaDatos />
            </PrivateRoute>
          }
        />
        <Route
          path="/carga-datos/confirmar"
          element={
            <PrivateRoute>
              <ConfirmarCarga />
            </PrivateRoute>
          }
        />
        <Route
          path="/carga-datos/errores"
          element={
            <PrivateRoute>
              <ErroresValidacion />
            </PrivateRoute>
          }
        />

        {/* Logout */}
        <Route path="/logout" element={<Logout />} />

        {/* Catch-all */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  );
}

// Wrapper para rutas privadas
function PrivateRoute({ children }) {
  return isLoggedIn() ? children : <Navigate to="/login" replace />;
}

// Componente principal
function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}

export default App;
