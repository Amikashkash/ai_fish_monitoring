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
  create: (data) => apiClient.post("/api/shipments/", data),
  getById: (id) => apiClient.get(`/api/shipments/${id}`),
  list: (params) => apiClient.get("/api/shipments/", { params }),
  update: (id, data) => apiClient.patch(`/api/shipments/${id}`, data),
  delete: (id) => apiClient.delete(`/api/shipments/${id}`)
};

// Treatments API
export const treatmentsAPI = {
  create: (data) => apiClient.post("/api/treatments/", data),
  getById: (id) => apiClient.get(`/api/treatments/${id}`),
  list: (activeOnly = false) => apiClient.get("/api/treatments/", { params: { active_only: activeOnly } }),
  update: (id, data) => apiClient.patch(`/api/treatments/${id}`, data),
  complete: (id) => apiClient.post(`/api/treatments/${id}/complete`),
  addDrug: (treatmentId, data) => apiClient.post(`/api/treatments/${treatmentId}/drugs`, data),
  removeDrug: (treatmentId, drugId) => apiClient.delete(`/api/treatments/${treatmentId}/drugs/${drugId}`)
};

// Observations API
export const observationsAPI = {
  create: (data) => apiClient.post("/api/observations/", data),
  listByTreatment: (treatmentId) => apiClient.get(`/api/observations/treatment/${treatmentId}`),
  getToday: () => apiClient.get("/api/observations/today")
};

// Followups API
export const followupsAPI = {
  create: (data) => apiClient.post("/api/followups/", data),
  getByTreatment: (treatmentId) => apiClient.get(`/api/followups/treatment/${treatmentId}`)
};

// Protocols API
export const protocolsAPI = {
  list: () => apiClient.get("/api/protocols/"),
  getById: (id) => apiClient.get(`/api/protocols/${id}`),
  create: (data) => apiClient.post("/api/protocols/", data),
  update: (id, data) => apiClient.put(`/api/protocols/${id}`, data),
  delete: (id) => apiClient.delete(`/api/protocols/${id}`)
};

// Protocol Templates API
export const protocolTemplatesAPI = {
  list: (params) => apiClient.get("/api/protocol-templates/", { params }),
  getById: (id) => apiClient.get(`/api/protocol-templates/${id}`),
  getDetails: (id) => apiClient.get(`/api/protocol-templates/details/${id}`),
  create: (data) => apiClient.post("/api/protocol-templates/", data),
  update: (id, data) => apiClient.put(`/api/protocol-templates/${id}`, data),
  delete: (id) => apiClient.delete(`/api/protocol-templates/${id}`),
  updateUsage: (id, wasSuccessful) =>
    apiClient.post(`/api/protocol-templates/${id}/usage`, { was_successful: wasSuccessful }),
  recommendByPurpose: (purpose, params) =>
    apiClient.get("/api/protocol-templates/recommend/by-purpose", {
      params: { purpose, ...params }
    })
};

// Recommendations API
export const recommendationsAPI = {
  preShipment: (scientificName, sourceCountry) =>
    apiClient.get("/api/recommendations/pre-shipment", {
      params: { scientific_name: scientificName, source_country: sourceCountry }
    }),
  protocol: (shipmentId) =>
    apiClient.get(`/api/recommendations/protocol/${shipmentId}`)
};

// Suppliers API
export const suppliersAPI = {
  getScores: () => apiClient.get("/api/suppliers/scores")
};

// Tasks API
export const tasksAPI = {
  getDaily: () => apiClient.get("/api/tasks/daily")
};

// Excel Import API
export const excelImportAPI = {
  /**
   * Extract shipment data from Excel file using AI
   * @param {File} file - Excel file to process
   * @param {string} sheetName - Optional sheet name to analyze
   * @returns {Promise} - Extracted data with validation
   */
  extract: (file, sheetName = null) => {
    const formData = new FormData();
    formData.append("file", file);
    if (sheetName) {
      formData.append("sheet_name", sheetName);
    }
    return apiClient.post("/api/excel-import/extract", formData, {
      headers: {
        "Content-Type": "multipart/form-data"
      }
    });
  },

  /**
   * Extract data and optionally create shipment
   * @param {File} file - Excel file
   * @param {boolean} autoCreate - Whether to auto-create shipment
   * @returns {Promise} - Extracted data and shipment ID if created
   */
  extractAndCreate: (file, autoCreate = false) => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("auto_create", autoCreate);
    return apiClient.post("/api/excel-import/extract-and-create-shipment", formData, {
      headers: {
        "Content-Type": "multipart/form-data"
      }
    });
  },

  /**
   * Get supported Excel formats and tips
   * @returns {Promise} - Supported formats info
   */
  getSupportedFormats: () => apiClient.get("/api/excel-import/supported-formats")
};

export default apiClient;
