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

        <!-- Supplier / invoice footnote -->
        <div v-if="t.supplierName || t.invoiceNumber" class="footnote">
          <span v-if="t.supplierName">{{ t.supplierName }}</span>
          <span v-if="t.invoiceNumber"> · #{{ t.invoiceNumber }}</span>
        </div>

        <!-- Actions -->
        <div class="card-actions">
          <router-link :to="`/checklist/${t.id}`" class="btn btn-obs">
            Record Observation
          </router-link>
          <button
            v-if="t.status === 'active'"
            @click="complete(t)"
            class="btn btn-complete"
          >
            Mark Complete
          </button>
        </div>
      </div>
    </div>

    <div v-else class="empty-state">
      <p>{{ showAll ? "No treatments found" : "No active treatments" }}</p>
      <router-link to="/shipments-list" class="btn btn-obs" style="display:inline-block;margin-top:1rem;">
        Go to Shipments
      </router-link>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from "vue";
import { treatmentsAPI, shipmentsAPI, protocolsAPI } from "../api/client";

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
          daysActive: daysActive(t),
          protocolNames,
        };
      })
    );

    const complete = async (t) => {
      const name = t.commonName || t.scientificName || `Treatment #${t.id}`;
      if (!confirm(`Mark treatment for ${name} as complete?`)) return;
      try {
        await treatmentsAPI.complete(t.id);
        await load();
      } catch (e) {
        alert("Failed to mark treatment as complete.");
      }
    };

    onMounted(load);

    return { loading, showAll, enriched, load, complete };
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
</style>
