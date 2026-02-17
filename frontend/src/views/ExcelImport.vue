<template>
  <div class="excel-page">
    <div class="page-header">
      <h2>Import Shipment from Invoice</h2>
      <p class="subtitle">Upload a proforma or commercial invoice and the AI will extract all fish species automatically.</p>
    </div>

    <!-- Draft Resume Banner -->
    <div v-if="hasDraft && !extracted" class="draft-banner">
      <span>You have an unsaved import from before. Resume it?</span>
      <button class="btn-link" @click="loadDraft">Resume</button>
      <button class="btn-link danger" @click="clearDraft">Discard</button>
    </div>

    <!-- Upload Area -->
    <div class="card upload-card" v-if="!extracted">
      <div
        class="drop-zone"
        :class="{ dragging }"
        @dragover.prevent="dragging = true"
        @dragleave="dragging = false"
        @drop.prevent="onDrop"
        @click="$refs.fileInput.click()"
      >
        <div class="drop-icon">📄</div>
        <p class="drop-text">Drag & drop your Excel invoice here</p>
        <p class="drop-hint">or click to browse</p>
        <p class="drop-formats">Supported: .xlsx, .xls</p>
        <input ref="fileInput" type="file" accept=".xlsx,.xls" @change="onFileSelect" hidden />
      </div>

      <div v-if="selectedFile" class="selected-file">
        <span class="file-icon">📊</span>
        <span class="file-name">{{ selectedFile.name }}</span>
        <span class="file-size">({{ (selectedFile.size / 1024).toFixed(1) }} KB)</span>
      </div>

      <div class="upload-actions" v-if="selectedFile">
        <button class="btn-primary" @click="extractData" :disabled="loading">
          {{ loading ? 'AI is reading your invoice...' : 'Extract Shipment Data with AI' }}
        </button>
        <button class="btn-secondary" @click="clearFile">Clear</button>
      </div>

      <div v-if="loading" class="loading-bar">
        <div class="loading-fill"></div>
      </div>
      <p v-if="error" class="error-msg">{{ error }}</p>
    </div>

    <!-- Edit & Confirm Section -->
    <div v-if="extracted" class="result-section">

      <!-- Shared Invoice Info -->
      <div class="card info-card">
        <div class="card-title-row">
          <h3>Invoice Details</h3>
          <span class="confidence-badge" :class="extracted.confidence">
            AI Confidence: {{ extracted.confidence || 'n/a' }}
          </span>
        </div>
        <div class="info-grid">
          <div class="info-item">
            <label class="info-label">Supplier *</label>
            <input v-model="extracted.supplier_name" class="editable-field" placeholder="Enter supplier name" />
          </div>
          <div class="info-item">
            <label class="info-label">Source Country *</label>
            <input v-model="extracted.source_country" class="editable-field" placeholder="e.g. Indonesia" />
          </div>
          <div class="info-item">
            <label class="info-label">Invoice Number</label>
            <input v-model="extracted.invoice_number" class="editable-field" placeholder="INV-2026-001" />
          </div>
          <div class="info-item">
            <label class="info-label">Arrival Date</label>
            <input v-model="extracted.shipment_date" type="date" class="editable-field" />
          </div>
        </div>
      </div>

      <!-- Per-Species Table -->
      <div class="card species-card">
        <div class="species-header">
          <h3>Fish Species — one shipment record per row</h3>
          <span class="total-fish">Total: {{ totalFish }} fish</span>
        </div>
        <p class="species-hint">
          Fill in <strong>Aquarium #</strong> (e.g. Tank 3, QT-1) and <strong>Tank Vol (L)</strong> for each species. You can leave Aquarium # blank and assign it later.
        </p>

        <div class="species-table">
          <!-- Header -->
          <div class="tbl-header">
            <span>Scientific Name *</span>
            <span>Common Name</span>
            <span>Qty *</span>
            <span>Aquarium #</span>
            <span>Tank Vol (L)</span>
            <span>Size</span>
            <span>Price/unit</span>
            <span></span>
          </div>

          <!-- Rows -->
          <div
            v-for="(row, idx) in extracted.fish_species"
            :key="idx"
            class="tbl-row"
            :class="{ 'row-invalid': !row.scientific_name || !row.quantity }"
          >
            <input v-model="row.scientific_name" class="cell" placeholder="Genus species" @input="saveDraft" />
            <input v-model="row.common_name" class="cell" placeholder="Common name" @input="saveDraft" />
            <input v-model.number="row.quantity" type="number" min="1" class="cell narrow" @input="saveDraft" />
            <input v-model="row.aquarium_number" class="cell narrow" placeholder="e.g. Tank 3" @input="saveDraft" />
            <input v-model.number="row.aquarium_volume_liters" type="number" min="1" class="cell narrow" placeholder="e.g. 200" @input="saveDraft" />
            <input v-model="row.size" class="cell narrow" placeholder="3-4cm" @input="saveDraft" />
            <input v-model.number="row.price_per_unit" type="number" step="0.01" class="cell narrow" placeholder="0.00" @input="saveDraft" />
            <button class="btn-remove" @click="removeRow(idx)" title="Remove this species">✕</button>
          </div>
        </div>

        <button class="btn-add-row" @click="addRow">+ Add species row</button>
      </div>

      <!-- Validation Warnings -->
      <div v-if="validationWarnings.length" class="warnings-box">
        <strong>Issues to review:</strong>
        <ul>
          <li v-for="w in validationWarnings" :key="w">{{ w }}</li>
        </ul>
      </div>

      <!-- Action Buttons -->
      <div class="result-actions">
        <button class="btn-primary" @click="createAllShipments" :disabled="creating || !canCreate">
          {{ creating ? `Creating... (${createProgress}/${extracted.fish_species.length})` : `Create ${extracted.fish_species.length} Shipment(s)` }}
        </button>
        <button class="btn-secondary" @click="startOver">Upload Different Invoice</button>
      </div>

      <!-- Creation Results -->
      <div v-if="createdShipments.length" class="success-box">
        <p class="success-msg">✓ Created {{ createdShipments.length }} shipment(s) successfully!</p>
        <ul class="created-list">
          <li v-for="s in createdShipments" :key="s.id">
            <strong>{{ s.scientific_name }}</strong>
            — {{ s.quantity }} fish
            <span v-if="s.aquarium_number"> → {{ s.aquarium_number }}</span>
            <span class="shipment-id">#{{ s.id }}</span>
          </li>
        </ul>
        <div class="success-actions">
          <router-link to="/treatments" class="btn-primary">Go to Treatments</router-link>
          <router-link to="/shipments-list" class="btn-secondary">View All Shipments</router-link>
        </div>
      </div>

      <p v-if="createError" class="error-msg">{{ createError }}</p>
    </div>
  </div>
</template>

<script>
import { excelImportAPI, shipmentsAPI } from "../api/client.js";

const DRAFT_KEY = "fish_import_draft";

export default {
  name: "ExcelImport",
  data() {
    return {
      selectedFile: null,
      dragging: false,
      loading: false,
      creating: false,
      createProgress: 0,
      error: "",
      createError: "",
      extracted: null,
      createdShipments: [],
      hasDraft: false
    };
  },
  computed: {
    totalFish() {
      if (!this.extracted?.fish_species) return 0;
      return this.extracted.fish_species.reduce((sum, s) => sum + (s.quantity || 0), 0);
    },
    validationWarnings() {
      if (!this.extracted) return [];
      const warnings = [];
      if (!this.extracted.supplier_name) warnings.push("Supplier name is missing");
      if (!this.extracted.source_country) warnings.push("Source country is missing");
      this.extracted.fish_species.forEach((s, i) => {
        if (!s.scientific_name) warnings.push(`Row ${i + 1}: Scientific name is required`);
        if (!s.quantity || s.quantity <= 0) warnings.push(`Row ${i + 1}: Quantity must be > 0`);
      });
      return warnings;
    },
    canCreate() {
      if (!this.extracted?.fish_species?.length) return false;
      return this.extracted.fish_species.every(s => s.scientific_name && s.quantity > 0)
        && this.extracted.source_country;
    }
  },
  mounted() {
    this.hasDraft = !!localStorage.getItem(DRAFT_KEY);
  },
  methods: {
    onDrop(e) {
      this.dragging = false;
      const file = e.dataTransfer.files[0];
      if (file) this.setFile(file);
    },
    onFileSelect(e) {
      const file = e.target.files[0];
      if (file) this.setFile(file);
    },
    setFile(file) {
      if (!file.name.match(/\.(xlsx|xls)$/i)) {
        this.error = "Please upload an Excel file (.xlsx or .xls)";
        return;
      }
      this.selectedFile = file;
      this.error = "";
    },
    clearFile() {
      this.selectedFile = null;
      this.error = "";
      this.$refs.fileInput.value = "";
    },
    async extractData() {
      if (!this.selectedFile) return;
      this.loading = true;
      this.error = "";
      try {
        const res = await excelImportAPI.extract(this.selectedFile);
        if (!res.data.success) {
          this.error = res.data.error || "Extraction failed";
          return;
        }
        const d = res.data.data;
        // Normalize species rows
        d.fish_species = (d.fish_species || []).map(s => ({
          scientific_name: s.scientific_name || "",
          common_name: s.common_name || "",
          quantity: s.quantity || 0,
          size: s.size || "",
          price_per_unit: s.price_per_unit || null,
          aquarium_number: "",
          aquarium_volume_liters: null
        }));
        this.extracted = d;
        this.saveDraft();
      } catch (e) {
        this.error = e.response?.data?.detail || "Failed to process file. Please try again.";
      } finally {
        this.loading = false;
      }
    },
    saveDraft() {
      if (this.extracted) {
        localStorage.setItem(DRAFT_KEY, JSON.stringify(this.extracted));
        this.hasDraft = true;
      }
    },
    loadDraft() {
      const raw = localStorage.getItem(DRAFT_KEY);
      if (raw) {
        this.extracted = JSON.parse(raw);
        this.hasDraft = false;
      }
    },
    clearDraft() {
      localStorage.removeItem(DRAFT_KEY);
      this.hasDraft = false;
    },
    addRow() {
      this.extracted.fish_species.push({
        scientific_name: "",
        common_name: "",
        quantity: 0,
        size: "",
        price_per_unit: null,
        aquarium_number: "",
        aquarium_volume_liters: null
      });
      this.saveDraft();
    },
    removeRow(idx) {
      this.extracted.fish_species.splice(idx, 1);
      this.saveDraft();
    },
    async createAllShipments() {
      this.creating = true;
      this.createProgress = 0;
      this.createError = "";
      this.createdShipments = [];

      const today = new Date().toISOString().split("T")[0];
      const errors = [];

      for (const species of this.extracted.fish_species) {
        try {
          const payload = {
            scientific_name: species.scientific_name,
            common_name: species.common_name || undefined,
            source: this.extracted.source_country || "Unknown",
            quantity: species.quantity,
            date: this.extracted.shipment_date || today,
            fish_size: species.size || undefined,
            price_per_fish: species.price_per_unit || undefined,
            aquarium_number: species.aquarium_number || undefined,
            aquarium_volume_liters: species.aquarium_volume_liters || undefined,
            invoice_number: this.extracted.invoice_number || undefined,
            supplier_name: this.extracted.supplier_name || undefined,
            notes: this.extracted.additional_notes || undefined
          };
          const res = await shipmentsAPI.create(payload);
          this.createdShipments.push(res.data);
          this.createProgress++;
        } catch (e) {
          const detail = e.response?.data?.detail;
          const msg = Array.isArray(detail)
            ? detail.map(d => `${d.loc?.slice(-1)[0]}: ${d.msg}`).join("; ")
            : (typeof detail === "string" ? detail : e.message);
          errors.push(`${species.scientific_name}: ${msg}`);
          this.createProgress++;
        }
      }

      this.creating = false;
      if (errors.length) {
        this.createError = "Some shipments failed:\n" + errors.join("\n");
      }
      if (this.createdShipments.length) {
        localStorage.removeItem(DRAFT_KEY);
        this.hasDraft = false;
      }
    },
    startOver() {
      this.extracted = null;
      this.selectedFile = null;
      this.error = "";
      this.createError = "";
      this.createdShipments = [];
      this.createProgress = 0;
      this.clearDraft();
    }
  }
};
</script>

<style scoped>
.excel-page { max-width: 1100px; margin: 0 auto; }
.page-header { margin-bottom: 1.5rem; }
.page-header h2 { font-size: 1.5rem; color: #1e293b; margin-bottom: 0.25rem; }
.subtitle { color: #64748b; font-size: 0.95rem; }

.draft-banner {
  background: #fffbeb; border: 1px solid #fbbf24; border-radius: 0.5rem;
  padding: 0.75rem 1rem; margin-bottom: 1rem; display: flex; align-items: center; gap: 1rem;
}
.btn-link { background: none; border: none; cursor: pointer; color: #0284c7; font-weight: 600; text-decoration: underline; }
.btn-link.danger { color: #dc2626; }

.card { background: white; border-radius: 0.75rem; padding: 1.5rem; box-shadow: 0 1px 4px rgba(0,0,0,0.1); margin-bottom: 1.5rem; }
.card-title-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.card-title-row h3 { font-size: 1.1rem; color: #1e293b; margin: 0; }

.drop-zone {
  border: 2px dashed #cbd5e1; border-radius: 0.75rem; padding: 3rem 1rem;
  text-align: center; cursor: pointer; transition: all 0.2s;
}
.drop-zone:hover, .drop-zone.dragging { border-color: #0ea5e9; background: #f0f9ff; }
.drop-icon { font-size: 3rem; margin-bottom: 0.75rem; }
.drop-text { font-size: 1.1rem; color: #334155; font-weight: 600; }
.drop-hint { color: #64748b; font-size: 0.9rem; }
.drop-formats { color: #94a3b8; font-size: 0.8rem; margin-top: 0.5rem; }

.selected-file { display: flex; align-items: center; gap: 0.5rem; margin-top: 1rem; padding: 0.75rem; background: #f0f9ff; border-radius: 0.5rem; }
.file-icon { font-size: 1.5rem; }
.file-name { font-weight: 600; color: #0284c7; }
.file-size { color: #64748b; font-size: 0.85rem; }

.upload-actions { display: flex; gap: 0.75rem; margin-top: 1rem; }

.loading-bar { height: 4px; background: #e2e8f0; border-radius: 2px; margin-top: 1rem; overflow: hidden; }
.loading-fill { height: 100%; width: 60%; background: #0ea5e9; animation: slide 1.5s infinite; }
@keyframes slide { 0% { transform: translateX(-100%); } 100% { transform: translateX(250%); } }

.info-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem; }
.info-item { display: flex; flex-direction: column; gap: 0.3rem; }
.info-label { font-size: 0.8rem; font-weight: 600; color: #64748b; }
.editable-field { border: 1px solid #e2e8f0; border-radius: 0.4rem; padding: 0.45rem 0.6rem; font-size: 0.9rem; outline: none; }
.editable-field:focus { border-color: #0ea5e9; }

.confidence-badge { padding: 0.3rem 0.75rem; border-radius: 1rem; font-size: 0.8rem; font-weight: 600; }
.confidence-badge.high { background: #dcfce7; color: #16a34a; }
.confidence-badge.medium { background: #fef9c3; color: #b45309; }
.confidence-badge.low { background: #fee2e2; color: #dc2626; }

.species-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }
.species-header h3 { font-size: 1rem; color: #1e293b; margin: 0; }
.total-fish { background: #dbeafe; color: #1d4ed8; padding: 0.25rem 0.75rem; border-radius: 1rem; font-size: 0.85rem; font-weight: 600; }
.species-hint { color: #64748b; font-size: 0.85rem; margin-bottom: 1rem; }

.species-table { overflow-x: auto; }
.tbl-header, .tbl-row {
  display: grid;
  grid-template-columns: 2fr 1.2fr 0.6fr 0.9fr 0.8fr 0.7fr 0.7fr 0.3fr;
  gap: 0.4rem; align-items: center; padding: 0.3rem 0;
}
.tbl-header { font-size: 0.75rem; font-weight: 700; color: #64748b; border-bottom: 2px solid #e2e8f0; padding-bottom: 0.5rem; margin-bottom: 0.25rem; }
.tbl-row { border-bottom: 1px solid #f1f5f9; }
.tbl-row.row-invalid { background: #fff7f7; }

.cell { border: 1px solid #e2e8f0; border-radius: 0.35rem; padding: 0.35rem 0.4rem; font-size: 0.85rem; width: 100%; box-sizing: border-box; }
.cell:focus { outline: none; border-color: #0ea5e9; }
.cell.narrow { text-align: center; }

.btn-remove { background: none; border: none; color: #94a3b8; cursor: pointer; font-size: 0.9rem; padding: 0.2rem 0.4rem; border-radius: 0.25rem; }
.btn-remove:hover { color: #dc2626; background: #fee2e2; }

.btn-add-row { margin-top: 0.75rem; background: none; border: 1px dashed #cbd5e1; color: #64748b; padding: 0.4rem 1rem; border-radius: 0.5rem; cursor: pointer; font-size: 0.85rem; }
.btn-add-row:hover { border-color: #0ea5e9; color: #0284c7; }

.warnings-box { background: #fffbeb; border: 1px solid #fbbf24; border-radius: 0.5rem; padding: 0.75rem 1rem; margin-bottom: 1rem; }
.warnings-box ul { margin: 0.5rem 0 0 1.25rem; font-size: 0.9rem; }

.result-actions { display: flex; gap: 0.75rem; flex-wrap: wrap; margin-bottom: 1rem; }

.success-box { background: #f0fdf4; border: 1px solid #86efac; border-radius: 0.75rem; padding: 1.25rem; }
.success-msg { color: #16a34a; font-weight: 600; font-size: 1rem; margin-bottom: 0.75rem; }
.created-list { margin: 0 0 1rem 1.25rem; font-size: 0.9rem; color: #374151; }
.created-list li { margin-bottom: 0.3rem; }
.shipment-id { color: #94a3b8; font-size: 0.8rem; margin-left: 0.5rem; }
.success-actions { display: flex; gap: 0.75rem; flex-wrap: wrap; }

.btn-primary { background: #0ea5e9; color: white; border: none; padding: 0.65rem 1.25rem; border-radius: 0.5rem; cursor: pointer; font-size: 0.95rem; font-weight: 600; text-decoration: none; display: inline-block; }
.btn-primary:hover { background: #0284c7; }
.btn-primary:disabled { opacity: 0.6; cursor: default; }
.btn-secondary { background: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; padding: 0.65rem 1.25rem; border-radius: 0.5rem; cursor: pointer; font-size: 0.95rem; text-decoration: none; display: inline-block; }
.btn-secondary:hover { background: #e2e8f0; }

.error-msg { color: #dc2626; margin-top: 0.75rem; font-size: 0.9rem; white-space: pre-line; }
</style>
