import axios from "axios";

// Opcional: puedes configurar un axios instance
const api = axios.create({
  baseURL: "/",         // Aquí queda “/” porque el proxy lo mapea al backend
  headers: {
    "Content-Type": "application/json",
  },
});

export function fetchCertificados() {
  return api.get("/api/certificados/");
}

export function subirExcel(formData) {
  return api.post("/api/carga-excel/", formData);
}