<template>
  <div class="shipments-page">
    <div class="page-header">
      <h2>Shipments</h2>
      <div class="header-actions">
        <router-link to="/import" class="btn-primary">Import Invoice</router-link>
        <router-link to="/shipments" class="btn-secondary">Add Manually</router-link>
      </div>
    </div>

    <div v-if="loading" class="loading-msg">Loading shipments...</div>
    <div v-else-if="error" class="error-msg">{{ error }}</div>

    <div v-else-if="!shipments.length" class="empty-state">
      <p>No shipments yet.</p>
      <router-link to="/import" class="btn-primary">Import your first invoice</router-link>
    </div>

    <div v-else>
      <div class="shipments-grid">
        <div v-for="s in shipments" :key="s.id" class="shipment-card">
          <div class="card-top">
            <div class="card-title">
              <p class="sci-name">{{ s.scientific_name }}</p>
              <p class="common-name">{{ s.common_name && s.common_name !== s.scientific_name ? s.common_name : '' }}</p>
            </div>
            <div class="card-badges">
              <span class="aquarium-badge" v-if="s.aquarium_number">{{ s.aquarium_number }}</span>
              <span class="status-badge no-tank" v-else>No tank assigned</span>
            </div>
          </div>

          <div class="card-details">
            <div class="detail">
              <span class="detail-label">Source</span>
              <span>{{ s.source }}</span>
            </div>
            <div class="detail">
              <span class="detail-label">Quantity</span>
              <span>{{ s.quantity }} fish</span>
            </div>
            <div class="detail">
              <span class="detail-label">Arrived</span>
              <span>{{ s.date }}</span>
            </div>
            <div class="detail" v-if="s.aquarium_volume_liters && s.aquarium_volume_liters > 1">
              <span class="detail-label">Tank Vol</span>
              <span>{{ s.aquarium_volume_liters }}L</span>
            </div>
            <div class="detail" v-if="s.fish_size">
              <span class="detail-label">Size</span>
              <span>{{ s.fish_size }}</span>
            </div>
            <div class="detail" v-if="s.supplier_name">
              <span class="detail-label">Supplier</span>
              <span>{{ s.supplier_name }}</span>
            </div>
            <div class="detail" v-if="s.invoice_number">
              <span class="detail-label">Invoice</span>
              <span>{{ s.invoice_number }}</span>
            </div>
          </div>

          <div class="card-actions">
            <button class="btn-treat" @click="openTreatModal(s)">Start Treatment</button>
            <button class="btn-edit" @click="openEditModal(s)" title="Edit shipment details">Edit</button>
            <button class="btn-delete" @click="confirmDelete(s)" title="Delete (DOA / shipping issue)">Delete</button>
          </div>
        </div>
      </div>

      <div class="pagination" v-if="total > pageSize">
        <button :disabled="page <= 1" @click="loadPage(page - 1)" class="btn-page">← Prev</button>
        <span>Page {{ page }} of {{ Math.ceil(total / pageSize) }}</span>
        <button :disabled="page * pageSize >= total" @click="loadPage(page + 1)" class="btn-page">Next →</button>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="deleteTarget" class="modal-backdrop" @click.self="deleteTarget = null">
      <div class="modal">
        <h3>Delete Shipment?</h3>
        <p class="modal-fish">
          <span v-if="deleteTarget.common_name && deleteTarget.common_name !== deleteTarget.scientific_name">
            {{ deleteTarget.common_name }} —
          </span>
          <em>{{ deleteTarget.scientific_name }}</em> — {{ deleteTarget.quantity }} fish
        </p>
        <p class="modal-warn">This cannot be undone. Use this for DOA, shipping problems, or data entry errors.</p>
        <div class="modal-reason">
          <label>Reason (optional)</label>
          <select v-model="deleteReason">
            <option value="">Select reason...</option>
            <option value="DOA">DOA – Dead on Arrival</option>
            <option value="Refused">Refused – poor condition</option>
            <option value="Wrong species">Wrong species received</option>
            <option value="Entry error">Data entry error</option>
            <option value="Other">Other</option>
          </select>
        </div>
        <div class="modal-actions">
          <button class="btn-delete-confirm" @click="doDelete" :disabled="deleting">
            {{ deleting ? 'Deleting...' : 'Yes, Delete' }}
          </button>
          <button class="btn-cancel" @click="deleteTarget = null">Cancel</button>
        </div>
        <p v-if="deleteError" class="error-msg">{{ deleteError }}</p>
      </div>
    </div>

    <!-- Start Treatment Modal -->
    <div v-if="treatTarget" class="modal-backdrop" @click.self="closeTreatModal">
      <div class="modal modal-wide">
        <h3>Start Treatment</h3>
        <p class="modal-fish">
          <span v-if="treatTarget.common_name && treatTarget.common_name !== treatTarget.scientific_name">
            {{ treatTarget.common_name }} —
          </span>
          <em>{{ treatTarget.scientific_name }}</em> — {{ treatTarget.quantity }} fish
        </p>

        <div class="treat-form">
          <!-- Aquarium assignment -->
          <div class="form-section">
            <h4>Aquarium Assignment</h4>
            <div class="form-row">
              <div class="form-group">
                <label>Aquarium / Tank # *</label>
                <input v-model="treatForm.aquarium_number" placeholder="e.g. Tank 3, QT-1" class="form-input" />
              </div>
              <div class="form-group">
                <label>Tank Volume (Liters) *</label>
                <input v-model.number="treatForm.aquarium_volume_liters" type="number" min="1" placeholder="e.g. 200" class="form-input" />
              </div>
            </div>
            <p class="density-hint" v-if="treatForm.aquarium_volume_liters > 0">
              Density: {{ (treatTarget.quantity / treatForm.aquarium_volume_liters).toFixed(2) }} fish/L
            </p>
          </div>

          <!-- Drug selection -->
          <div class="form-section">
            <h4>Treatment Drugs <span class="optional-label">(optional – add later)</span></h4>
            <div v-if="protocols.length" class="drug-list">
              <label v-for="p in protocols" :key="p.id" class="drug-checkbox">
                <input type="checkbox" :value="p.id" v-model="selectedProtocols" />
                <span class="drug-name">{{ p.drug_name }}</span>
                <span class="drug-info" v-if="p.standard_dosage">{{ p.standard_dosage }} {{ p.dosage_unit }}</span>
              </label>
            </div>
            <p v-else class="no-drugs">No drug protocols defined yet. You can add drugs from Drug Protocols tab.</p>
          </div>

          <!-- Date -->
          <div class="form-section">
            <div class="form-group">
              <label>Treatment Start Date</label>
              <input v-model="treatForm.start_date" type="date" class="form-input" />
            </div>
          </div>
        </div>

        <div class="modal-actions">
          <button class="btn-treat-confirm" @click="doStartTreatment" :disabled="treating || !treatForm.aquarium_number || !treatForm.aquarium_volume_liters">
            {{ treating ? 'Starting...' : 'Start Treatment' }}
          </button>
          <button class="btn-cancel" @click="closeTreatModal">Cancel</button>
        </div>
        <p v-if="treatError" class="error-msg">{{ treatError }}</p>
      </div>
    </div>
    <!-- Edit Shipment Modal -->
    <div v-if="editTarget" class="modal-backdrop" @click.self="editTarget = null">
      <div class="modal modal-wide">
        <h3>Edit Shipment</h3>
        <p class="modal-fish">
          <em>{{ editTarget.scientific_name }}</em>
        </p>
        <div class="treat-form">
          <div class="form-section">
            <div class="form-row">
              <div class="form-group">
                <label>Arrival Date</label>
                <input v-model="editForm.date" type="date" class="form-input" />
              </div>
              <div class="form-group">
                <label>Source Country</label>
                <input v-model="editForm.source" type="text" class="form-input" placeholder="e.g. Thailand" />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Scientific Name</label>
                <input v-model="editForm.scientific_name" type="text" class="form-input" />
              </div>
              <div class="form-group">
                <label>Common Name</label>
                <input v-model="editForm.common_name" type="text" class="form-input" />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Quantity</label>
                <input v-model.number="editForm.quantity" type="number" min="1" class="form-input" />
              </div>
              <div class="form-group">
                <label>Fish Size</label>
                <input v-model="editForm.fish_size" type="text" class="form-input" placeholder="e.g. 3-5cm" />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Supplier</label>
                <input v-model="editForm.supplier_name" type="text" class="form-input" />
              </div>
              <div class="form-group">
                <label>Invoice #</label>
                <input v-model="editForm.invoice_number" type="text" class="form-input" />
              </div>
            </div>
          </div>
        </div>
        <div class="modal-actions">
          <button class="btn-treat-confirm" @click="doEdit" :disabled="editing">
            {{ editing ? 'Saving...' : 'Save Changes' }}
          </button>
          <button class="btn-cancel" @click="editTarget = null">Cancel</button>
        </div>
        <p v-if="editError" class="error-msg">{{ editError }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import { shipmentsAPI, treatmentsAPI, protocolsAPI } from "../api/client.js";

export default {
  name: "ShipmentsList",
  data() {
    return {
      shipments: [],
      total: 0,
      page: 1,
      pageSize: 20,
      loading: true,
      error: "",
      // Delete
      deleteTarget: null,
      deleteReason: "",
      deleting: false,
      deleteError: "",
      // Treat
      treatTarget: null,
      protocols: [],
      selectedProtocols: [],
      treatForm: {
        aquarium_number: "",
        aquarium_volume_liters: null,
        start_date: new Date().toISOString().split("T")[0]
      },
      treating: false,
      treatError: "",
      // Edit
      editTarget: null,
      editForm: {},
      editing: false,
      editError: ""
    };
  },
  mounted() {
    this.loadPage(1);
    this.loadProtocols();
  },
  methods: {
    async loadPage(p) {
      this.loading = true;
      this.error = "";
      try {
        const skip = (p - 1) * this.pageSize;
        const res = await shipmentsAPI.list({ skip, limit: this.pageSize });
        this.shipments = res.data.shipments;
        this.total = res.data.total;
        this.page = p;
      } catch (e) {
        this.error = e.response?.data?.detail || "Failed to load shipments.";
      } finally {
        this.loading = false;
      }
    },
    async loadProtocols() {
      try {
        const res = await protocolsAPI.list();
        this.protocols = res.data;
      } catch {
        // silent — drug protocols are optional
      }
    },

    // ── Delete ──
    confirmDelete(shipment) {
      this.deleteTarget = shipment;
      this.deleteReason = "";
      this.deleteError = "";
    },
    async doDelete() {
      this.deleting = true;
      this.deleteError = "";
      try {
        await shipmentsAPI.delete(this.deleteTarget.id);
        this.shipments = this.shipments.filter(s => s.id !== this.deleteTarget.id);
        this.total--;
        this.deleteTarget = null;
      } catch (e) {
        this.deleteError = e.response?.data?.detail || "Failed to delete.";
      } finally {
        this.deleting = false;
      }
    },

    // ── Start Treatment ──
    openTreatModal(shipment) {
      this.treatTarget = shipment;
      this.treatError = "";
      this.selectedProtocols = [];
      this.treatForm = {
        aquarium_number: shipment.aquarium_number || "",
        aquarium_volume_liters: shipment.aquarium_volume_liters > 1 ? shipment.aquarium_volume_liters : null,
        start_date: new Date().toISOString().split("T")[0]
      };
    },
    closeTreatModal() {
      this.treatTarget = null;
      this.treatError = "";
    },
    // ── Edit ──
    openEditModal(shipment) {
      this.editTarget = shipment;
      this.editError = "";
      this.editForm = {
        date: shipment.date || "",
        scientific_name: shipment.scientific_name || "",
        common_name: shipment.common_name || "",
        source: shipment.source || "",
        quantity: shipment.quantity,
        fish_size: shipment.fish_size || "",
        supplier_name: shipment.supplier_name || "",
        invoice_number: shipment.invoice_number || "",
      };
    },
    async doEdit() {
      this.editing = true;
      this.editError = "";
      try {
        const patch = {};
        for (const [k, v] of Object.entries(this.editForm)) {
          if (v !== "" && v != null) patch[k] = v;
        }
        await shipmentsAPI.update(this.editTarget.id, patch);
        const idx = this.shipments.findIndex(s => s.id === this.editTarget.id);
        if (idx >= 0) Object.assign(this.shipments[idx], patch);
        this.editTarget = null;
      } catch (e) {
        this.editError = e.response?.data?.detail || "Failed to save changes.";
      } finally {
        this.editing = false;
      }
    },

    async doStartTreatment() {
      if (!this.treatForm.aquarium_number || !this.treatForm.aquarium_volume_liters) return;
      this.treating = true;
      this.treatError = "";
      try {
        // 1. Update shipment with aquarium info
        await shipmentsAPI.update(this.treatTarget.id, {
          aquarium_number: this.treatForm.aquarium_number,
          aquarium_volume_liters: this.treatForm.aquarium_volume_liters
        });

        // 2. Create treatment with selected drugs
        const drugs = this.selectedProtocols.map(id => ({ drug_protocol_id: id }));
        await treatmentsAPI.create({
          shipment_id: this.treatTarget.id,
          start_date: this.treatForm.start_date,
          drugs
        });

        // 3. Update local shipment card + close modal
        const idx = this.shipments.findIndex(s => s.id === this.treatTarget.id);
        if (idx >= 0) {
          this.shipments[idx].aquarium_number = this.treatForm.aquarium_number;
          this.shipments[idx].aquarium_volume_liters = this.treatForm.aquarium_volume_liters;
        }
        this.closeTreatModal();
        this.$router.push("/treatments");
      } catch (e) {
        const detail = e.response?.data?.detail;
        this.treatError = typeof detail === "string" ? detail : (e.message || "Failed to start treatment.");
      } finally {
        this.treating = false;
      }
    }
  }
};
</script>

<style scoped>
.shipments-page { max-width: 1100px; margin: 0 auto; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 0.75rem; }
.page-header h2 { font-size: 1.5rem; color: #1e293b; margin: 0; }
.header-actions { display: flex; gap: 0.5rem; }

.loading-msg { text-align: center; color: #64748b; padding: 2rem; }
.error-msg { color: #dc2626; margin-top: 0.5rem; font-size: 0.9rem; }
.empty-state { text-align: center; padding: 3rem; color: #64748b; }
.empty-state p { margin-bottom: 1rem; font-size: 1.1rem; }

.shipments-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem; }

.shipment-card {
  background: white; border-radius: 0.75rem; padding: 1.25rem;
  box-shadow: 0 1px 4px rgba(0,0,0,0.1); display: flex; flex-direction: column; gap: 0.75rem;
}
.card-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 0.5rem; }
.sci-name { font-weight: 700; color: #1e293b; font-style: italic; margin: 0; }
.common-name { color: #64748b; font-size: 0.85rem; margin: 0.2rem 0 0; }
.card-badges { display: flex; flex-direction: column; align-items: flex-end; gap: 0.3rem; flex-shrink: 0; }
.aquarium-badge { background: #0ea5e9; color: white; font-size: 0.75rem; font-weight: 700; padding: 0.25rem 0.6rem; border-radius: 1rem; }
.status-badge.no-tank { background: #f1f5f9; color: #94a3b8; font-size: 0.7rem; padding: 0.2rem 0.5rem; border-radius: 1rem; }

.card-details { display: grid; grid-template-columns: 1fr 1fr; gap: 0.4rem; }
.detail { display: flex; flex-direction: column; }
.detail-label { font-size: 0.7rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; }
.detail span:last-child { font-size: 0.85rem; color: #374151; }

.card-actions { display: flex; gap: 0.5rem; border-top: 1px solid #f1f5f9; padding-top: 0.75rem; }
.btn-treat { flex: 1; background: #0ea5e9; color: white; border: none; padding: 0.45rem 0.75rem; border-radius: 0.4rem; cursor: pointer; font-size: 0.85rem; font-weight: 600; }
.btn-treat:hover { background: #0284c7; }
.btn-edit { background: #f0fdf4; color: #166534; border: 1px solid #bbf7d0; padding: 0.45rem 0.75rem; border-radius: 0.4rem; cursor: pointer; font-size: 0.85rem; }
.btn-edit:hover { background: #dcfce7; }
.btn-delete { background: #fff1f2; color: #e11d48; border: 1px solid #fecdd3; padding: 0.45rem 0.75rem; border-radius: 0.4rem; cursor: pointer; font-size: 0.85rem; }
.btn-delete:hover { background: #ffe4e6; }

.pagination { display: flex; justify-content: center; align-items: center; gap: 1rem; margin-top: 1.5rem; }
.btn-page { background: #f1f5f9; border: 1px solid #cbd5e1; color: #475569; padding: 0.5rem 1rem; border-radius: 0.5rem; cursor: pointer; }
.btn-page:disabled { opacity: 0.4; cursor: default; }

/* Modal */
.modal-backdrop {
  position: fixed; inset: 0; background: rgba(0,0,0,0.4);
  display: flex; align-items: center; justify-content: center; z-index: 100; padding: 1rem;
}
.modal {
  background: white; border-radius: 0.75rem; padding: 1.75rem;
  width: 100%; max-width: 420px; box-shadow: 0 10px 40px rgba(0,0,0,0.2);
}
.modal-wide { max-width: 580px; }
.modal h3 { font-size: 1.2rem; color: #1e293b; margin: 0 0 0.5rem; }
.modal-fish { font-weight: 600; font-style: italic; color: #0284c7; margin: 0 0 0.75rem; }
.modal-warn { color: #64748b; font-size: 0.9rem; margin-bottom: 1rem; }
.modal-reason { margin-bottom: 1.25rem; }
.modal-reason label { display: block; font-size: 0.85rem; font-weight: 600; color: #64748b; margin-bottom: 0.35rem; }
.modal-reason select { width: 100%; padding: 0.5rem; border: 1px solid #e2e8f0; border-radius: 0.4rem; font-size: 0.9rem; }
.modal-actions { display: flex; gap: 0.75rem; margin-top: 1.25rem; }
.btn-delete-confirm { flex: 1; background: #e11d48; color: white; border: none; padding: 0.6rem 1rem; border-radius: 0.5rem; cursor: pointer; font-weight: 600; }
.btn-delete-confirm:hover { background: #be123c; }
.btn-delete-confirm:disabled { opacity: 0.6; cursor: default; }
.btn-cancel { flex: 1; background: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; padding: 0.6rem 1rem; border-radius: 0.5rem; cursor: pointer; }

/* Treat modal */
.treat-form { display: flex; flex-direction: column; gap: 1.25rem; }
.form-section { background: #f8fafc; border-radius: 0.5rem; padding: 1rem; }
.form-section h4 { font-size: 0.9rem; color: #1e293b; margin: 0 0 0.75rem; font-weight: 700; }
.optional-label { color: #94a3b8; font-weight: 400; font-size: 0.8rem; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }
.form-group { display: flex; flex-direction: column; gap: 0.3rem; }
.form-group label { font-size: 0.8rem; font-weight: 600; color: #64748b; }
.form-input { border: 1px solid #e2e8f0; border-radius: 0.4rem; padding: 0.5rem 0.65rem; font-size: 0.9rem; outline: none; width: 100%; box-sizing: border-box; }
.form-input:focus { border-color: #0ea5e9; }
.density-hint { margin-top: 0.5rem; font-size: 0.8rem; color: #0284c7; font-weight: 600; }

.drug-list { display: flex; flex-direction: column; gap: 0.5rem; max-height: 180px; overflow-y: auto; }
.drug-checkbox { display: flex; align-items: center; gap: 0.5rem; cursor: pointer; padding: 0.35rem 0.5rem; border-radius: 0.35rem; }
.drug-checkbox:hover { background: #e0f2fe; }
.drug-name { font-size: 0.9rem; font-weight: 500; color: #1e293b; flex: 1; }
.drug-info { font-size: 0.8rem; color: #64748b; }
.no-drugs { font-size: 0.85rem; color: #94a3b8; }

.btn-treat-confirm { flex: 1; background: #0ea5e9; color: white; border: none; padding: 0.65rem 1rem; border-radius: 0.5rem; cursor: pointer; font-weight: 600; font-size: 0.95rem; }
.btn-treat-confirm:hover { background: #0284c7; }
.btn-treat-confirm:disabled { opacity: 0.5; cursor: default; }

.btn-primary { background: #0ea5e9; color: white; border: none; padding: 0.55rem 1.1rem; border-radius: 0.5rem; cursor: pointer; font-size: 0.9rem; font-weight: 600; text-decoration: none; display: inline-block; }
.btn-primary:hover { background: #0284c7; }
.btn-secondary { background: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; padding: 0.55rem 1.1rem; border-radius: 0.5rem; cursor: pointer; font-size: 0.9rem; text-decoration: none; display: inline-block; }
.btn-secondary:hover { background: #e2e8f0; }
</style>
