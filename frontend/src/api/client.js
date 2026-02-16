/**
 * API client for Fish Monitoring System backend
 */

import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json"
  }
});

// Shipments API
export const shipmentsAPI = {
  create: (data) => apiClient.post("/api/shipments", data),
  getById: (id) => apiClient.get(\),
  list: (params) => apiClient.get("/api/shipments", { params })
};

// Treatments API
export const treatmentsAPI = {
  create: (data) => apiClient.post("/api/treatments", data),
  getById: (id) => apiClient.get(\),
  list: (activeOnly = false) => apiClient.get("/api/treatments", { params: { active_only: activeOnly } }),
  complete: (id) => apiClient.post(\)
};

// Observations API
export const observationsAPI = {
  create: (data) => apiClient.post("/api/observations", data),
  listByTreatment: (treatmentId) => apiClient.get(\)
};

// Followups API
export const followupsAPI = {
  create: (data) => apiClient.post("/api/followups", data),
  getByTreatment: (treatmentId) => apiClient.get(\)
};

// Protocols API
export const protocolsAPI = {
  list: () => apiClient.get("/api/protocols"),
  getById: (id) => apiClient.get(\),
  create: (data) => apiClient.post("/api/protocols", data)
};

// Recommendations API
export const recommendationsAPI = {
  preShipment: (scientificName, sourceCountry) => 
    apiClient.get("/api/recommendations/pre-shipment", {
      params: { scientific_name: scientificName, source_country: sourceCountry }
    }),
  protocol: (shipmentId) => 
    apiClient.get(\)
};

// Suppliers API
export const suppliersAPI = {
  getScores: () => apiClient.get("/api/suppliers/scores")
};

// Tasks API
export const tasksAPI = {
  getDaily: () => apiClient.get("/api/tasks/daily")
};

export default apiClient;
