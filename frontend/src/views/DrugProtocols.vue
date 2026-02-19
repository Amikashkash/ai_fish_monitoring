<template>
  <div class="protocols-page">
    <div class="page-header">
      <h2>Drug Protocols</h2>
      <button v-if="isAdmin" class="btn-primary" @click="openAddForm">+ Add Protocol</button>
    </div>

    <!-- Add / Edit Form -->
    <div v-if="showForm" class="card form-card">
      <h3>{{ editingId ? "Edit Protocol" : "New Drug Protocol" }}</h3>
      <form @submit.prevent="submitProtocol">
        <div class="form-row">
          <div class="form-group">
            <label>Drug Name *</label>
            <input v-model="form.drug_name" type="text" placeholder="e.g. Dabitetracyclin" required />
          </div>
          <div class="form-group">
            <label>Dosage Unit *</label>
            <input v-model="form.dosage_unit" type="text" placeholder="e.g. gr/100L, mg/L" required />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>Min Dosage</label>
            <input v-model.number="form.dosage_min" type="number" step="0.01" placeholder="5.0" />
          </div>
          <div class="form-group">
            <label>Max Dosage</label>
            <input v-model.number="form.dosage_max" type="number" step="0.01" placeholder="10.0" />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>Frequency</label>
            <select v-model="form.frequency">
              <option value="daily">Daily</option>
              <option value="twice_daily">Twice Daily</option>
              <option value="every_other_day">Every Other Day</option>
              <option value="weekly">Weekly</option>
              <option value="once">Once</option>
            </select>
          </div>
          <div class="form-group">
            <label>Typical Treatment Period (days)</label>
            <input v-model.number="form.typical_treatment_period_days" type="number" placeholder="10" />
          </div>
        </div>
        <div class="form-group">
          <label>Notes / Instructions</label>
          <textarea v-model="form.notes" rows="3" placeholder="e.g. Reduce dosage by half after third day."></textarea>
        </div>
        <div class="form-actions">
          <button type="submit" class="btn-primary" :disabled="submitting">
            {{ submitting ? "Saving..." : (editingId ? "Update Protocol" : "Save Protocol") }}
          </button>
          <button type="button" class="btn-secondary" @click="cancelForm">Cancel</button>
        </div>
        <p v-if="formError" class="error-msg">{{ formError }}</p>
        <p v-if="formSuccess" class="success-msg">{{ formSuccess }}</p>
      </form>
    </div>

    <!-- Protocols List -->
    <div v-if="loading" class="loading">Loading protocols...</div>
    <div v-else-if="protocols.length === 0 && !showForm" class="empty-state">
      <p>No drug protocols yet.</p>
      <button class="btn-primary" @click="openAddForm">Add Your First Protocol</button>
    </div>
    <div v-else class="protocols-grid">
      <div v-for="protocol in protocols" :key="protocol.id" class="protocol-card">
        <div class="protocol-header">
          <h3>{{ protocol.drug_name }}</h3>
          <div class="card-actions" v-if="isAdmin">
            <button class="btn-icon btn-edit" @click="openEditForm(protocol)" title="Edit">✏️</button>
            <button class="btn-icon btn-delete" @click="deleteProtocol(protocol)" title="Delete">🗑</button>
          </div>
        </div>
        <div class="protocol-details">
          <div class="detail-row">
            <span class="label">Dosage</span>
            <span class="value">
              {{ protocol.dosage_min }}
              <span v-if="protocol.dosage_max && protocol.dosage_max !== protocol.dosage_min">– {{ protocol.dosage_max }}</span>
              {{ protocol.dosage_unit }}
            </span>
          </div>
          <div class="detail-row" v-if="protocol.frequency">
            <span class="label">Frequency</span>
            <span class="value">{{ formatFrequency(protocol.frequency) }}</span>
          </div>
          <div class="detail-row" v-if="protocol.typical_treatment_period_days">
            <span class="label">Duration</span>
            <span class="value">{{ protocol.typical_treatment_period_days }} days</span>
          </div>
          <div class="notes" v-if="protocol.notes">
            <span class="label">Notes:</span> {{ protocol.notes }}
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="deletingProtocol" class="modal-overlay" @click.self="deletingProtocol = null">
      <div class="modal">
        <h3>Delete Protocol</h3>
        <p>Are you sure you want to delete <strong>{{ deletingProtocol.drug_name }}</strong>?</p>
        <p class="warn-text">This cannot be undone. Existing treatments using this protocol won't be affected.</p>
        <div class="modal-actions">
          <button class="btn-danger" @click="confirmDelete" :disabled="deleting">
            {{ deleting ? "Deleting..." : "Yes, Delete" }}
          </button>
          <button class="btn-secondary" @click="deletingProtocol = null">Cancel</button>
        </div>
        <p v-if="deleteError" class="error-msg">{{ deleteError }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import { protocolsAPI } from "../api/client.js";
import { useAuth } from "../composables/useAuth.js";

export default {
  name: "DrugProtocols",
  setup() {
    const { isAdmin } = useAuth();
    return { isAdmin };
  },
  data() {
    return {
      protocols: [],
      loading: true,
      showForm: false,
      editingId: null,
      submitting: false,
      formError: "",
      formSuccess: "",
      deletingProtocol: null,
      deleting: false,
      deleteError: "",
      form: this.blankForm()
    };
  },
  async mounted() {
    await this.loadProtocols();
  },
  methods: {
    blankForm() {
      return {
        drug_name: "",
        dosage_min: null,
        dosage_max: null,
        dosage_unit: "",
        frequency: "daily",
        typical_treatment_period_days: null,
        notes: ""
      };
    },
    async loadProtocols() {
      this.loading = true;
      try {
        const res = await protocolsAPI.list();
        this.protocols = res.data;
      } catch (e) {
        console.error("Failed to load protocols", e);
      } finally {
        this.loading = false;
      }
    },
    openAddForm() {
      this.editingId = null;
      this.form = this.blankForm();
      this.formError = "";
      this.formSuccess = "";
      this.showForm = true;
      this.$nextTick(() => window.scrollTo({ top: 0, behavior: "smooth" }));
    },
    openEditForm(protocol) {
      this.editingId = protocol.id;
      this.form = {
        drug_name: protocol.drug_name,
        dosage_min: protocol.dosage_min,
        dosage_max: protocol.dosage_max,
        dosage_unit: protocol.dosage_unit,
        frequency: protocol.frequency || "daily",
        typical_treatment_period_days: protocol.typical_treatment_period_days,
        notes: protocol.notes || ""
      };
      this.formError = "";
      this.formSuccess = "";
      this.showForm = true;
      this.$nextTick(() => window.scrollTo({ top: 0, behavior: "smooth" }));
    },
    async submitProtocol() {
      this.submitting = true;
      this.formError = "";
      this.formSuccess = "";
      try {
        if (this.editingId) {
          await protocolsAPI.update(this.editingId, this.form);
          this.formSuccess = "Protocol updated!";
        } else {
          await protocolsAPI.create(this.form);
          this.formSuccess = "Protocol saved!";
        }
        await this.loadProtocols();
        setTimeout(() => this.cancelForm(), 1200);
      } catch (e) {
        this.formError = e.response?.data?.detail || "Failed to save protocol.";
      } finally {
        this.submitting = false;
      }
    },
    cancelForm() {
      this.showForm = false;
      this.editingId = null;
      this.formError = "";
      this.formSuccess = "";
      this.form = this.blankForm();
    },
    deleteProtocol(protocol) {
      this.deletingProtocol = protocol;
      this.deleteError = "";
    },
    async confirmDelete() {
      this.deleting = true;
      this.deleteError = "";
      try {
        await protocolsAPI.delete(this.deletingProtocol.id);
        this.protocols = this.protocols.filter(p => p.id !== this.deletingProtocol.id);
        this.deletingProtocol = null;
      } catch (e) {
        this.deleteError = e.response?.data?.detail || "Failed to delete protocol.";
      } finally {
        this.deleting = false;
      }
    },
    formatFrequency(freq) {
      const map = {
        daily: "Daily",
        twice_daily: "Twice Daily",
        every_other_day: "Every Other Day",
        weekly: "Weekly",
        once: "Once"
      };
      return map[freq] || freq;
    }
  }
};
</script>

<style scoped>
.protocols-page { max-width: 900px; margin: 0 auto; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
.page-header h2 { font-size: 1.5rem; color: #1e293b; }

.card { background: white; border-radius: 0.75rem; padding: 1.5rem; box-shadow: 0 1px 4px rgba(0,0,0,0.1); margin-bottom: 1.5rem; }
.form-card h3 { margin-bottom: 1rem; color: #0284c7; }

.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.form-group { display: flex; flex-direction: column; gap: 0.4rem; margin-bottom: 1rem; }
.form-group label { font-size: 0.85rem; font-weight: 600; color: #475569; }
.form-group input, .form-group select, .form-group textarea {
  padding: 0.6rem 0.75rem; border: 1px solid #cbd5e1; border-radius: 0.5rem;
  font-size: 0.95rem; outline: none; transition: border-color 0.2s; font-family: inherit;
}
.form-group input:focus, .form-group select:focus, .form-group textarea:focus { border-color: #0ea5e9; }

.form-actions { display: flex; gap: 0.75rem; margin-top: 0.5rem; }

.btn-primary { background: #0ea5e9; color: white; border: none; padding: 0.6rem 1.25rem; border-radius: 0.5rem; cursor: pointer; font-size: 0.95rem; font-weight: 600; }
.btn-primary:hover { background: #0284c7; }
.btn-primary:disabled { opacity: 0.6; cursor: default; }
.btn-secondary { background: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; padding: 0.6rem 1.25rem; border-radius: 0.5rem; cursor: pointer; font-size: 0.95rem; }
.btn-secondary:hover { background: #e2e8f0; }
.btn-danger { background: #dc2626; color: white; border: none; padding: 0.6rem 1.25rem; border-radius: 0.5rem; cursor: pointer; font-size: 0.95rem; font-weight: 600; }
.btn-danger:hover { background: #b91c1c; }
.btn-danger:disabled { opacity: 0.6; cursor: default; }

.error-msg { color: #dc2626; margin-top: 0.5rem; font-size: 0.9rem; }
.success-msg { color: #16a34a; margin-top: 0.5rem; font-size: 0.9rem; }

.loading { text-align: center; padding: 2rem; color: #64748b; }
.empty-state { text-align: center; padding: 3rem; color: #64748b; }
.empty-state p { margin-bottom: 1rem; font-size: 1.1rem; }

.protocols-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1rem; }
.protocol-card { background: white; border-radius: 0.75rem; padding: 1.25rem; box-shadow: 0 1px 4px rgba(0,0,0,0.1); }

.protocol-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
  gap: 0.5rem;
}
.protocol-header h3 { font-size: 1.1rem; color: #0284c7; margin: 0; }

.card-actions { display: flex; gap: 0.3rem; flex-shrink: 0; }
.btn-icon {
  background: none;
  border: 1px solid #e2e8f0;
  border-radius: 0.4rem;
  padding: 0.25rem 0.45rem;
  cursor: pointer;
  font-size: 0.9rem;
  line-height: 1;
  transition: background 0.15s;
}
.btn-edit:hover { background: #eff6ff; border-color: #bfdbfe; }
.btn-delete:hover { background: #fef2f2; border-color: #fecaca; }

.detail-row { display: flex; justify-content: space-between; padding: 0.3rem 0; border-bottom: 1px solid #f1f5f9; }
.label { font-size: 0.82rem; color: #64748b; font-weight: 600; }
.value { font-size: 0.9rem; color: #1e293b; font-weight: 500; }
.notes { margin-top: 0.75rem; font-size: 0.85rem; color: #475569; line-height: 1.4; }
.notes .label { color: #64748b; font-weight: 600; }

/* Modal */
.modal-overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex; align-items: center; justify-content: center;
  z-index: 100; padding: 1rem;
}
.modal {
  background: white; border-radius: 0.75rem;
  padding: 1.5rem; max-width: 420px; width: 100%;
  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
}
.modal h3 { margin: 0 0 0.75rem 0; font-size: 1.15rem; color: #1e293b; }
.modal p { margin: 0 0 0.5rem 0; color: #374151; font-size: 0.95rem; }
.warn-text { font-size: 0.82rem; color: #9ca3af; }
.modal-actions { display: flex; gap: 0.75rem; margin-top: 1.25rem; }

@media (max-width: 600px) {
  .form-row { grid-template-columns: 1fr; }
  .page-header { flex-direction: column; align-items: flex-start; gap: 0.75rem; }
}
</style>
