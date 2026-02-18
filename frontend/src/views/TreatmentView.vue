<template>
  <div class="treatment-view">
    <div class="view-header">
      <h2>Treatments</h2>
      <label class="show-all-toggle">
        <input type="checkbox" v-model="showAll" @change="load" />
        Show completed
      </label>
    </div>

    <div v-if="loading" class="loading">Loading treatments...</div>

    <div v-else-if="enriched.length" class="treatment-list">
      <div
        v-for="t in enriched"
        :key="t.id"
        class="treatment-card"
        :class="t.status"
      >
        <!-- Header: species name + status badge -->
        <div class="card-header">
          <div class="species-names">
            <h3>{{ t.commonName || t.scientificName || "Unknown species" }}</h3>
            <span v-if="t.commonName && t.scientificName" class="sci-name">
              {{ t.scientificName }}
            </span>
          </div>
          <span class="status-badge" :class="t.status">{{ t.status }}</span>
        </div>

        <!-- Info grid -->
        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">Aquarium</span>
            <span class="info-val aquarium-val">{{ t.aquariumNumber || "—" }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Fish</span>
            <span class="info-val">{{ t.quantity != null ? t.quantity : "—" }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Tank vol.</span>
            <span class="info-val">{{ t.volumeLabel }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Density</span>
            <span class="info-val">{{ t.densityLabel }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Source</span>
            <span class="info-val">{{ t.source || "—" }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Started</span>
            <span class="info-val">{{ t.start_date }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Days active</span>
            <span class="info-val days-val" :class="{ warning: t.daysActive > 14 }">
              {{ t.daysActive }} days
            </span>
          </div>
          <div v-if="t.end_date" class="info-item">
            <span class="info-label">Ended</span>
            <span class="info-val">{{ t.end_date }}</span>
          </div>
        </div>

        <!-- Drug protocols -->
        <div v-if="t.protocolNames.length" class="protocols-row">
          <span class="info-label">Protocols:</span>
          <span
            v-for="name in t.protocolNames"
            :key="name"
            class="proto-tag"
          >{{ name }}</span>
        </div>

        <!-- Protocol completion alert -->
        <div v-if="t.protocolDue" class="protocol-due-alert">
          ✓ Protocol complete — {{ t.daysActive }} of {{ t.maxProtocolDays }} days done. Ready to mark as complete?
        </div>

        <!-- Supplier / invoice footnote -->
        <div v-if="t.supplierName || t.invoiceNumber" class="footnote">
          <span v-if="t.supplierName">{{ t.supplierName }}</span>
          <span v-if="t.invoiceNumber"> · #{{ t.invoiceNumber }}</span>
        </div>

        <!-- Outcome summary (completed treatments) -->
        <div v-if="t.status === 'completed' && t.outcome" class="outcome-summary">
          <span class="outcome-label" :class="t.outcome">{{ outcomeLabel(t.outcome) }}</span>
          <span v-if="t.outcome_score" class="outcome-stars">{{ '★'.repeat(t.outcome_score) }}{{ '☆'.repeat(5 - t.outcome_score) }}</span>
          <span v-if="t.total_mortality" class="outcome-mortality">{{ t.total_mortality }} dead</span>
        </div>

        <!-- Actions -->
        <div class="card-actions">
          <router-link :to="`/checklist/${t.id}`" class="btn btn-obs">
            Record Observation
          </router-link>
          <button
            v-if="t.status === 'active'"
            @click="toggleEdit(t.id)"
            class="btn btn-edit-drugs"
            :class="{ active: expandedId === t.id }"
          >
            {{ expandedId === t.id ? "Done Editing" : "Edit Drugs" }}
          </button>
          <button
            @click="toggleDetails(t)"
            class="btn btn-edit-details"
            :class="{ active: detailsId === t.id }"
          >
            {{ detailsId === t.id ? "Cancel" : "Edit Details" }}
          </button>
          <button
            v-if="t.status === 'active'"
            @click="openGraduate(t)"
            class="btn btn-complete"
          >
            Graduate Fish
          </button>
        </div>

        <!-- Inline drug editor -->
        <div v-if="expandedId === t.id" class="drug-editor">
          <div class="drug-editor-title">Drug Protocols</div>

          <!-- Current drugs -->
          <div v-if="t.drugs && t.drugs.length" class="current-drugs">
            <div v-for="d in t.drugs" :key="d.id" class="drug-row">
              <span class="drug-name">{{ protocolMap[d.drug_protocol_id]?.drug_name || `Protocol #${d.drug_protocol_id}` }}</span>
              <span v-if="d.actual_dosage" class="drug-dose">{{ d.actual_dosage }}</span>
              <button class="btn-remove-drug" @click="removeDrug(t, d.id)" title="Remove">✕</button>
            </div>
          </div>
          <p v-else class="no-drugs">No drugs assigned yet.</p>

          <!-- Add drug row -->
          <div class="add-drug-row">
            <select v-model="drugForm.drug_protocol_id" class="drug-select">
              <option value="" disabled>Select protocol...</option>
              <option
                v-for="p in allProtocols"
                :key="p.id"
                :value="p.id"
              >{{ p.drug_name }}</option>
            </select>
            <input
              v-model.number="drugForm.actual_dosage"
              type="number"
              step="0.01"
              placeholder="Dosage"
              class="dosage-input"
            />
            <button
              class="btn-add-drug"
              :disabled="!drugForm.drug_protocol_id || drugSaving"
              @click="addDrug(t)"
            >
              {{ drugSaving ? "Adding..." : "+ Add" }}
            </button>
          </div>
          <p v-if="drugError" class="drug-error">{{ drugError }}</p>
        </div>

        <!-- Inline details editor -->
        <div v-if="detailsId === t.id" class="details-editor">
          <div class="drug-editor-title">Aquarium Details</div>
          <div class="details-grid">
            <div class="details-field">
              <label>Aquarium #</label>
              <input v-model="detailsForm.aquarium_number" type="text" placeholder="e.g. A-12" />
            </div>
            <div class="details-field">
              <label>Tank Volume (L)</label>
              <input v-model.number="detailsForm.aquarium_volume_liters" type="number" step="1" min="0" placeholder="e.g. 200" />
            </div>
            <div class="details-field">
              <label>Fish Count</label>
              <input v-model.number="detailsForm.quantity" type="number" min="0" placeholder="e.g. 50" />
            </div>
            <div class="details-field">
              <label>Treatment Started</label>
              <input v-model="detailsForm.start_date" type="date" :max="new Date().toISOString().slice(0,10)" />
            </div>
          </div>
          <div class="details-actions">
            <button class="btn-save-details" :disabled="detailsSaving" @click="saveDetails(t)">
              {{ detailsSaving ? "Saving..." : "Save" }}
            </button>
            <button class="btn-cancel-details" @click="detailsId = null">Cancel</button>
          </div>
          <p v-if="detailsError" class="drug-error">{{ detailsError }}</p>
          <p v-if="detailsSaved" class="details-saved">Saved!</p>
        </div>
      </div>
    </div>

    <div v-else class="empty-state">
      <p>{{ showAll ? "No treatments found" : "No active treatments" }}</p>
      <router-link to="/shipments-list" class="btn btn-obs" style="display:inline-block;margin-top:1rem;">
        Go to Shipments
      </router-link>
    </div>

    <!-- Graduate Modal -->
    <div v-if="graduateTarget" class="modal-backdrop" @click.self="graduateTarget = null">
      <div class="modal">
        <h3>Graduate Fish</h3>
        <p class="modal-sub">
          {{ graduateTarget.commonName || graduateTarget.scientificName }}
          · {{ graduateTarget.daysActive }} days in quarantine
        </p>

        <div class="grad-form">
          <div class="grad-field">
            <label>End Date</label>
            <input v-model="graduateForm.end_date" type="date" :max="TODAY" />
          </div>

          <div class="grad-field">
            <label>Overall Outcome</label>
            <select v-model="graduateForm.outcome">
              <option value="">Select outcome...</option>
              <option value="healthy">Excellent – All fish healthy</option>
              <option value="minor_loss">Good – Minor losses (&lt; 10%)</option>
              <option value="major_loss">Fair – Significant losses (10–30%)</option>
              <option value="total_loss">Poor – Major losses (&gt; 30%)</option>
            </select>
          </div>

          <div class="grad-field">
            <label>Final Score</label>
            <div class="star-rating">
              <button
                v-for="n in 5" :key="n"
                @click="graduateForm.outcome_score = n"
                :class="{ filled: n <= graduateForm.outcome_score }"
                class="star-btn"
              >★</button>
            </div>
          </div>

          <div class="grad-field">
            <label>Total Fish Died (whole period)</label>
            <input v-model.number="graduateForm.total_mortality" type="number" min="0" :max="graduateTarget.quantity" placeholder="0" />
          </div>

          <div class="grad-field">
            <label>Notes for AI / future reference</label>
            <textarea v-model="graduateForm.outcome_notes" rows="3" placeholder="What worked, what didn't, any observations..."></textarea>
          </div>
        </div>

        <p class="grad-hint">This removes the fish from active monitoring. All observation history is preserved.</p>

        <div class="modal-actions">
          <button
            class="btn-graduate"
            @click="doGraduate"
            :disabled="graduating || !graduateForm.outcome || !graduateForm.outcome_score"
          >
            {{ graduating ? "Saving..." : "Confirm Graduation" }}
          </button>
          <button class="btn-cancel-grad" @click="graduateTarget = null">Cancel</button>
        </div>
        <p v-if="graduateError" class="grad-error">{{ graduateError }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from "vue";
import { treatmentsAPI, shipmentsAPI, protocolsAPI } from "../api/client";

const toInputDate = (d) => d ? d.slice(0, 10) : "";

export default {
  name: "TreatmentView",
  setup() {
    const loading = ref(true);
    const showAll = ref(false);
    const treatments = ref([]);
    const shipmentMap = ref({});
    const protocolMap = ref({});

    const load = async () => {
      loading.value = true;
      try {
        const [tRes, sRes, pRes] = await Promise.all([
          treatmentsAPI.list(!showAll.value),
          shipmentsAPI.list({ page_size: 200 }),
          protocolsAPI.list(),
        ]);

        treatments.value = tRes.data || [];

        const shipments = sRes.data?.shipments || sRes.data || [];
        shipmentMap.value = {};
        shipments.forEach(s => { shipmentMap.value[s.id] = s; });

        protocolMap.value = {};
        (pRes.data || []).forEach(p => { protocolMap.value[p.id] = p; });
      } catch (e) {
        console.error("Failed to load treatments:", e);
      } finally {
        loading.value = false;
      }
    };

    const daysActive = (t) => {
      const start = new Date(t.start_date);
      const end = t.end_date ? new Date(t.end_date) : new Date();
      return Math.max(0, Math.floor((end - start) / 86400000));
    };

    const enriched = computed(() =>
      treatments.value.map(t => {
        const s = shipmentMap.value[t.shipment_id] || {};
        const vol = s.aquarium_volume_liters;
        const qty = s.quantity;
        const density = vol && vol > 1 && qty ? (qty / vol).toFixed(2) : null;

        const protocolNames = (t.drugs || []).map(d => {
          const p = protocolMap.value[d.drug_protocol_id];
          return p?.name || p?.drug_name || `Protocol #${d.drug_protocol_id}`;
        });

        const days = daysActive(t);
        const protocolDays = (t.drugs || [])
          .map(d => protocolMap.value[d.drug_protocol_id]?.typical_treatment_period_days)
          .filter(d => d != null);
        const maxProtocolDays = protocolDays.length ? Math.max(...protocolDays) : null;
        const protocolDue = t.status === "active" && maxProtocolDays != null && days >= maxProtocolDays;

        return {
          ...t,
          commonName: s.common_name,
          scientificName: s.scientific_name,
          aquariumNumber: s.aquarium_number,
          quantity: s.quantity,
          source: s.source,
          supplierName: s.supplier_name,
          invoiceNumber: s.invoice_number,
          volumeLabel: vol && vol > 1 ? `${vol} L` : "—",
          densityLabel: density ? `${density} fish/L` : "—",
          daysActive: days,
          maxProtocolDays,
          protocolDue,
          protocolNames,
        };
      })
    );

    const TODAY = new Date().toISOString().slice(0, 10);

    const outcomeLabel = (o) => ({
      healthy:    "Excellent – All healthy",
      minor_loss: "Good – Minor losses",
      major_loss: "Fair – Significant losses",
      total_loss: "Poor – Major losses",
    }[o] || o);

    // Graduate modal state
    const graduateTarget = ref(null);
    const graduateForm = ref({ end_date: "", outcome: "", outcome_score: 0, total_mortality: 0, outcome_notes: "" });
    const graduating = ref(false);
    const graduateError = ref("");

    const openGraduate = (t) => {
      graduateTarget.value = t;
      graduateError.value = "";
      graduateForm.value = {
        end_date: TODAY,
        outcome: "",
        outcome_score: 0,
        total_mortality: 0,
        outcome_notes: "",
      };
    };

    const doGraduate = async () => {
      if (!graduateForm.value.outcome || !graduateForm.value.outcome_score) return;
      graduating.value = true;
      graduateError.value = "";
      try {
        await treatmentsAPI.update(graduateTarget.value.id, {
          status: "completed",
          end_date: graduateForm.value.end_date,
          outcome: graduateForm.value.outcome,
          outcome_score: graduateForm.value.outcome_score,
          total_mortality: graduateForm.value.total_mortality || 0,
          outcome_notes: graduateForm.value.outcome_notes || null,
        });
        graduateTarget.value = null;
        await load();
      } catch (e) {
        graduateError.value = e.response?.data?.detail || "Failed to graduate treatment.";
      } finally {
        graduating.value = false;
      }
    };

    // Drug editor state
    const expandedId = ref(null);
    const drugForm = ref({ drug_protocol_id: "", actual_dosage: null });
    const drugSaving = ref(false);
    const drugError = ref("");

    const allProtocols = computed(() => Object.values(protocolMap.value));

    const toggleEdit = (id) => {
      expandedId.value = expandedId.value === id ? null : id;
      drugForm.value = { drug_protocol_id: "", actual_dosage: null };
      drugError.value = "";
    };

    const addDrug = async (t) => {
      if (!drugForm.value.drug_protocol_id) return;
      drugSaving.value = true;
      drugError.value = "";
      try {
        await treatmentsAPI.addDrug(t.id, {
          drug_protocol_id: parseInt(drugForm.value.drug_protocol_id),
          actual_dosage: drugForm.value.actual_dosage || null,
        });
        drugForm.value = { drug_protocol_id: "", actual_dosage: null };
        await load();
      } catch (e) {
        drugError.value = e.response?.data?.detail || "Failed to add drug.";
      } finally {
        drugSaving.value = false;
      }
    };

    const removeDrug = async (t, drugId) => {
      try {
        await treatmentsAPI.removeDrug(t.id, drugId);
        await load();
      } catch (e) {
        alert("Failed to remove drug.");
      }
    };

    // Details editor state
    const detailsId = ref(null);
    const detailsForm = ref({ aquarium_number: "", aquarium_volume_liters: null, quantity: null, start_date: "" });
    const detailsSaving = ref(false);
    const detailsError = ref("");
    const detailsSaved = ref(false);

    const toggleDetails = (t) => {
      if (detailsId.value === t.id) {
        detailsId.value = null;
        return;
      }
      detailsId.value = t.id;
      detailsError.value = "";
      detailsSaved.value = false;
      const s = shipmentMap.value[t.shipment_id] || {};
      detailsForm.value = {
        aquarium_number: s.aquarium_number || "",
        aquarium_volume_liters: s.aquarium_volume_liters || null,
        quantity: s.quantity || null,
        start_date: toInputDate(t.start_date),
      };
    };

    const saveDetails = async (t) => {
      detailsSaving.value = true;
      detailsError.value = "";
      detailsSaved.value = false;
      try {
        const patch = {};
        if (detailsForm.value.aquarium_number !== "") patch.aquarium_number = detailsForm.value.aquarium_number;
        if (detailsForm.value.aquarium_volume_liters != null) patch.aquarium_volume_liters = detailsForm.value.aquarium_volume_liters;
        if (detailsForm.value.quantity != null) patch.quantity = detailsForm.value.quantity;
        await shipmentsAPI.update(t.shipment_id, patch);
        if (detailsForm.value.start_date) {
          await treatmentsAPI.update(t.id, { start_date: detailsForm.value.start_date });
        }
        await load();
        detailsSaved.value = true;
        setTimeout(() => { detailsSaved.value = false; detailsId.value = null; }, 1200);
      } catch (e) {
        detailsError.value = e.response?.data?.detail || "Failed to save details.";
      } finally {
        detailsSaving.value = false;
      }
    };

    onMounted(load);

    return {
      loading, showAll, enriched, load,
      TODAY, outcomeLabel,
      graduateTarget, graduateForm, graduating, graduateError, openGraduate, doGraduate,
      expandedId, drugForm, drugSaving, drugError,
      allProtocols, protocolMap, toggleEdit, addDrug, removeDrug,
      detailsId, detailsForm, detailsSaving, detailsError, detailsSaved,
      toggleDetails, saveDetails,
    };
  }
};
</script>

<style scoped>
.view-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.25rem;
}

.view-header h2 {
  margin: 0;
  font-size: 1.4rem;
  color: #1e3a5f;
}

.show-all-toggle {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.9rem;
  color: #374151;
  cursor: pointer;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: #6b7280;
}

/* Card */
.treatment-card {
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 2px 6px rgba(0,0,0,0.08);
  padding: 1.25rem;
  margin-bottom: 1rem;
  border-left: 4px solid #0ea5e9;
}

.treatment-card.completed {
  border-left-color: #10b981;
  opacity: 0.85;
}

/* Header */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.species-names h3 {
  margin: 0 0 0.2rem 0;
  font-size: 1.1rem;
  color: #111827;
}

.sci-name {
  font-size: 0.8rem;
  color: #6b7280;
  font-style: italic;
}

.status-badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.65rem;
  border-radius: 9999px;
  text-transform: capitalize;
  white-space: nowrap;
}

.status-badge.active {
  background: #dbeafe;
  color: #1d4ed8;
}

.status-badge.completed {
  background: #d1fae5;
  color: #065f46;
}

/* Info grid */
.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 0.6rem;
  margin-bottom: 0.9rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

.info-label {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #9ca3af;
}

.info-val {
  font-size: 0.95rem;
  font-weight: 600;
  color: #1f2937;
}

.aquarium-val {
  color: #0284c7;
}

.days-val {
  color: #059669;
}

.days-val.warning {
  color: #d97706;
}

/* Protocols */
.protocols-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.4rem;
  margin-bottom: 0.75rem;
}

.proto-tag {
  background: #eff6ff;
  color: #1d4ed8;
  font-size: 0.78rem;
  padding: 0.2rem 0.55rem;
  border-radius: 0.35rem;
  font-weight: 500;
}

/* Protocol due alert */
.protocol-due-alert {
  background: #fef9c3;
  border: 1px solid #fde047;
  border-radius: 0.5rem;
  padding: 0.6rem 0.9rem;
  font-size: 0.88rem;
  font-weight: 600;
  color: #854d0e;
  margin-bottom: 0.75rem;
}

/* Footnote */
.footnote {
  font-size: 0.78rem;
  color: #9ca3af;
  margin-bottom: 0.75rem;
}

/* Actions */
.card-actions {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
}

.btn {
  padding: 0.55rem 1.1rem;
  border-radius: 0.5rem;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  border: none;
  text-decoration: none;
  display: inline-block;
}

.btn-obs {
  background: #0ea5e9;
  color: white;
}

.btn-obs:hover {
  background: #0284c7;
}

.btn-complete {
  background: #10b981;
  color: white;
}

.btn-complete:hover {
  background: #059669;
}

/* Empty state */
.empty-state {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
}

/* Drug editor */
.btn-edit-drugs {
  background: #f0f9ff;
  color: #0369a1;
  border: 1px solid #bae6fd;
}
.btn-edit-drugs:hover { background: #e0f2fe; }
.btn-edit-drugs.active { background: #e0f2fe; border-color: #7dd3fc; }

.drug-editor {
  margin-top: 1rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 0.5rem;
  border: 1px solid #e2e8f0;
}

.drug-editor-title {
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #64748b;
  margin-bottom: 0.75rem;
}

.current-drugs {
  margin-bottom: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.drug-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 0.4rem;
  padding: 0.4rem 0.6rem;
}

.drug-name {
  flex: 1;
  font-size: 0.9rem;
  color: #1e293b;
  font-weight: 500;
}

.drug-dose {
  font-size: 0.82rem;
  color: #64748b;
}

.btn-remove-drug {
  background: none;
  border: none;
  color: #dc2626;
  cursor: pointer;
  font-size: 0.8rem;
  padding: 0.1rem 0.3rem;
  border-radius: 0.25rem;
  line-height: 1;
}
.btn-remove-drug:hover { background: #fef2f2; }

.no-drugs {
  font-size: 0.85rem;
  color: #94a3b8;
  margin: 0 0 0.75rem 0;
}

.add-drug-row {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  flex-wrap: wrap;
}

.drug-select {
  flex: 1;
  min-width: 150px;
  padding: 0.45rem 0.6rem;
  border: 1px solid #cbd5e1;
  border-radius: 0.4rem;
  font-size: 0.88rem;
  background: white;
  color: #1e293b;
}

.dosage-input {
  width: 90px;
  padding: 0.45rem 0.6rem;
  border: 1px solid #cbd5e1;
  border-radius: 0.4rem;
  font-size: 0.88rem;
}

.btn-add-drug {
  padding: 0.45rem 0.9rem;
  background: #0ea5e9;
  color: white;
  border: none;
  border-radius: 0.4rem;
  font-size: 0.88rem;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
}
.btn-add-drug:hover:not(:disabled) { background: #0284c7; }
.btn-add-drug:disabled { opacity: 0.5; cursor: not-allowed; }

.drug-error {
  font-size: 0.82rem;
  color: #dc2626;
  margin: 0.4rem 0 0 0;
}

/* Details editor */
.btn-edit-details {
  background: #f0fdf4;
  color: #166534;
  border: 1px solid #bbf7d0;
}
.btn-edit-details:hover { background: #dcfce7; }
.btn-edit-details.active { background: #dcfce7; border-color: #86efac; }

.details-editor {
  margin-top: 1rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 0.5rem;
  border: 1px solid #e2e8f0;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
  gap: 0.75rem;
  margin-bottom: 0.85rem;
}

.details-field {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.details-field label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.details-field input {
  padding: 0.45rem 0.6rem;
  border: 1px solid #cbd5e1;
  border-radius: 0.4rem;
  font-size: 0.9rem;
  background: white;
}

.details-field input:focus {
  outline: none;
  border-color: #0ea5e9;
}

.details-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-save-details {
  padding: 0.45rem 1rem;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 0.4rem;
  font-size: 0.88rem;
  font-weight: 600;
  cursor: pointer;
}
.btn-save-details:hover:not(:disabled) { background: #059669; }
.btn-save-details:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-cancel-details {
  padding: 0.45rem 0.9rem;
  background: #f1f5f9;
  color: #475569;
  border: 1px solid #cbd5e1;
  border-radius: 0.4rem;
  font-size: 0.88rem;
  cursor: pointer;
}
.btn-cancel-details:hover { background: #e2e8f0; }

.details-saved {
  font-size: 0.82rem;
  color: #10b981;
  font-weight: 600;
  margin: 0.4rem 0 0 0;
}

/* Outcome summary row */
.outcome-summary {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.45rem 0.75rem;
  background: #f0fdf4;
  border-radius: 0.4rem;
  margin-bottom: 0.5rem;
}
.outcome-label {
  font-size: 0.82rem;
  font-weight: 700;
}
.outcome-label.healthy    { color: #15803d; }
.outcome-label.minor_loss { color: #0369a1; }
.outcome-label.major_loss { color: #b45309; }
.outcome-label.total_loss { color: #b91c1c; }
.outcome-stars { color: #f59e0b; font-size: 0.95rem; letter-spacing: 0.05em; }
.outcome-mortality { font-size: 0.8rem; color: #dc2626; margin-left: auto; }

/* Graduate modal */
.modal-backdrop {
  position: fixed; inset: 0; background: rgba(0,0,0,0.45);
  display: flex; align-items: center; justify-content: center;
  z-index: 200; padding: 1rem;
}
.modal {
  background: white; border-radius: 0.75rem; padding: 1.75rem;
  width: 100%; max-width: 460px; box-shadow: 0 10px 40px rgba(0,0,0,0.2);
  max-height: 90vh; overflow-y: auto;
}
.modal h3 { font-size: 1.2rem; color: #1e293b; margin: 0 0 0.3rem; }
.modal-sub { font-size: 0.88rem; color: #64748b; margin: 0 0 1.25rem; }

.grad-form { display: flex; flex-direction: column; gap: 1rem; }
.grad-field { display: flex; flex-direction: column; gap: 0.3rem; }
.grad-field label { font-size: 0.78rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.04em; }
.grad-field input, .grad-field select, .grad-field textarea {
  padding: 0.5rem 0.65rem; border: 1px solid #e2e8f0; border-radius: 0.4rem;
  font-size: 0.9rem; background: white; color: #1e293b;
  font-family: inherit;
}
.grad-field input:focus, .grad-field select:focus, .grad-field textarea:focus {
  outline: none; border-color: #0ea5e9;
}
.grad-field textarea { resize: vertical; }

.star-rating { display: flex; gap: 0.25rem; }
.star-btn {
  background: none; border: none; font-size: 1.6rem;
  cursor: pointer; color: #d1d5db; transition: color 0.1s; padding: 0; line-height: 1;
}
.star-btn.filled { color: #f59e0b; }
.star-btn:hover { color: #f59e0b; }

.grad-hint {
  font-size: 0.8rem; color: #94a3b8; margin: 1rem 0 0; font-style: italic;
}

.modal-actions { display: flex; gap: 0.75rem; margin-top: 1.25rem; }
.btn-graduate {
  flex: 1; background: #10b981; color: white; border: none;
  padding: 0.65rem 1rem; border-radius: 0.5rem; cursor: pointer;
  font-weight: 700; font-size: 0.95rem;
}
.btn-graduate:hover:not(:disabled) { background: #059669; }
.btn-graduate:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-cancel-grad {
  flex: 1; background: #f1f5f9; color: #475569; border: 1px solid #cbd5e1;
  padding: 0.65rem 1rem; border-radius: 0.5rem; cursor: pointer; font-size: 0.9rem;
}
.btn-cancel-grad:hover { background: #e2e8f0; }
.grad-error { font-size: 0.85rem; color: #dc2626; margin: 0.5rem 0 0; }
</style>
