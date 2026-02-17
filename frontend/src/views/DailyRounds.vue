<template>
  <div class="daily-rounds">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h2>Daily Rounds</h2>
        <p class="today-label">{{ todayLabel }}</p>
      </div>
      <div class="summary-badges">
        <span class="badge badge-total">{{ cards.length }} active</span>
        <span class="badge badge-done">{{ doneCount }} done today</span>
        <span v-if="doneCount === cards.length && cards.length > 0" class="badge badge-all-done">All complete ✓</span>
      </div>
    </div>

    <div v-if="loading" class="loading">Loading treatments...</div>

    <div v-else-if="cards.length === 0" class="empty-state">
      <p>No active treatments today.</p>
      <router-link to="/shipments-list" class="btn-link">Go to Shipments to start a treatment</router-link>
    </div>

    <div v-else class="cards-list">
      <div
        v-for="card in cards"
        :key="card.treatmentId"
        class="round-card"
        :class="{ done: card.doneToday, saving: card.saving }"
      >
        <!-- Card header -->
        <div class="card-top">
          <div class="fish-info">
            <span class="aquarium-badge">{{ card.aquariumNumber || "No tank" }}</span>
            <h3>{{ card.commonName || card.scientificName }}</h3>
            <span v-if="card.commonName" class="sci">{{ card.scientificName }}</span>
          </div>
          <div class="card-meta">
            <span class="day-counter" :class="{ overdue: card.daysActive > card.treatmentDays }">
              Day {{ card.daysActive }} / {{ card.treatmentDays || "?" }}
            </span>
            <span v-if="card.doneToday" class="done-badge">✓ Done today</span>
          </div>
        </div>

        <!-- Drug protocols -->
        <div v-if="card.protocolNames.length" class="protocols-line">
          <span class="protocols-label">Today's drugs:</span>
          <span v-for="name in card.protocolNames" :key="name" class="proto-tag">{{ name }}</span>
        </div>

        <!-- Already done: show summary -->
        <div v-if="card.doneToday" class="done-summary">
          <div class="done-row">
            <span>Dose given: <strong>{{ card.todayObs.treatments_completed ? "Yes" : "No" }}</strong></span>
            <span v-if="card.todayObs.dead_fish_count">Dead today: <strong class="red">{{ card.todayObs.dead_fish_count }}</strong></span>
            <span v-if="card.todayObs.condition_trend" class="trend-chip" :class="card.todayObs.condition_trend">
              {{ trendLabel(card.todayObs.condition_trend) }}
            </span>
          </div>
          <p v-if="card.todayObs.notes" class="obs-notes">{{ card.todayObs.notes }}</p>
          <button class="btn-edit" @click="reopen(card)">Edit observation</button>
        </div>

        <!-- Observation form -->
        <div v-else class="obs-form">
          <!-- Dose checkbox -->
          <label class="dose-check">
            <input type="checkbox" v-model="card.form.treatments_completed" />
            <span>Dose administered today</span>
          </label>

          <!-- Dead fish -->
          <div class="field-row">
            <label class="field-label">Dead fish today</label>
            <input
              type="number"
              min="0"
              v-model.number="card.form.dead_fish_count"
              class="count-input"
              placeholder="0"
            />
          </div>

          <!-- Condition trend -->
          <div class="field-row">
            <label class="field-label">Condition</label>
            <div class="trend-buttons">
              <button
                v-for="opt in trendOptions"
                :key="opt.value"
                type="button"
                class="trend-btn"
                :class="[opt.value, { active: card.form.condition_trend === opt.value }]"
                @click="card.form.condition_trend = opt.value"
              >{{ opt.label }}</button>
            </div>
          </div>

          <!-- Quick symptoms -->
          <div class="symptoms-row">
            <label class="sym-check" v-for="sym in symptoms" :key="sym.key">
              <input type="checkbox" v-model="card.form[sym.key]" />
              <span>{{ sym.label }}</span>
            </label>
          </div>

          <!-- Notes -->
          <textarea
            v-model="card.form.notes"
            class="notes-input"
            rows="2"
            placeholder="Optional notes..."
          ></textarea>

          <div class="form-actions">
            <button class="btn-save" @click="save(card)" :disabled="card.saving">
              {{ card.saving ? "Saving..." : "Save Observation" }}
            </button>
          </div>

          <p v-if="card.error" class="error-msg">{{ card.error }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from "vue";
import { treatmentsAPI, shipmentsAPI, protocolsAPI, observationsAPI } from "../api/client";

const TODAY = new Date().toISOString().split("T")[0];

const SYMPTOMS = [
  { key: "symptoms_lethargy", label: "Lethargy" },
  { key: "symptoms_loss_of_appetite", label: "Poor appetite" },
  { key: "symptoms_spots", label: "Spots" },
  { key: "symptoms_fin_damage", label: "Fin damage" },
  { key: "symptoms_breathing_issues", label: "Breathing" },
];

const TREND_OPTIONS = [
  { value: "progress", label: "Improving" },
  { value: "same", label: "Same" },
  { value: "regress", label: "Worse" },
];

function blankForm(treatmentId) {
  return {
    treatment_id: treatmentId,
    observation_date: TODAY,
    treatments_completed: true,
    dead_fish_count: 0,
    condition_trend: "same",
    symptoms_lethargy: false,
    symptoms_loss_of_appetite: false,
    symptoms_spots: false,
    symptoms_fin_damage: false,
    symptoms_breathing_issues: false,
    notes: "",
  };
}

export default {
  name: "DailyRounds",
  setup() {
    const loading = ref(true);
    const cards = ref([]);

    const todayLabel = computed(() => {
      return new Date().toLocaleDateString("en-GB", {
        weekday: "long", day: "numeric", month: "long", year: "numeric"
      });
    });

    const doneCount = computed(() => cards.value.filter(c => c.doneToday).length);

    const load = async () => {
      loading.value = true;
      try {
        const [tRes, sRes, pRes, todayRes] = await Promise.all([
          treatmentsAPI.list(true),           // active only
          shipmentsAPI.list({ page_size: 200 }),
          protocolsAPI.list(),
          observationsAPI.getToday(),
        ]);

        const shipments = sRes.data?.shipments || sRes.data || [];
        const shipmentMap = {};
        shipments.forEach(s => { shipmentMap[s.id] = s; });

        const protocolMap = {};
        (pRes.data || []).forEach(p => { protocolMap[p.id] = p; });

        // Build set of treatment_ids that have today's obs
        const todayObsByTreatment = {};
        (todayRes.data || []).forEach(obs => {
          todayObsByTreatment[obs.treatment_id] = obs;
        });

        cards.value = (tRes.data || []).map(t => {
          const s = shipmentMap[t.shipment_id] || {};
          const protocolNames = (t.drugs || []).map(d => {
            const p = protocolMap[d.drug_protocol_id];
            return p?.drug_name || p?.name || `Protocol #${d.drug_protocol_id}`;
          });

          const startDate = new Date(t.start_date);
          const daysActive = Math.max(1, Math.floor((new Date() - startDate) / 86400000) + 1);

          // Find typical treatment period from any drug protocol
          let treatmentDays = null;
          for (const d of (t.drugs || [])) {
            const p = protocolMap[d.drug_protocol_id];
            if (p?.typical_treatment_period_days) {
              treatmentDays = p.typical_treatment_period_days;
              break;
            }
          }

          const todayObs = todayObsByTreatment[t.id] || null;

          return {
            treatmentId: t.id,
            shipmentId: t.shipment_id,
            scientificName: s.scientific_name || "Unknown",
            commonName: s.common_name,
            aquariumNumber: s.aquarium_number,
            quantity: s.quantity,
            source: s.source,
            protocolNames,
            daysActive,
            treatmentDays,
            start_date: t.start_date,
            doneToday: !!todayObs,
            todayObs,
            form: blankForm(t.id),
            saving: false,
            error: null,
          };
        });
      } catch (e) {
        console.error("Failed to load daily rounds:", e);
      } finally {
        loading.value = false;
      }
    };

    const save = async (card) => {
      card.saving = true;
      card.error = null;
      try {
        const payload = { ...card.form };
        // Remove empty optional fields
        if (!payload.dead_fish_count) delete payload.dead_fish_count;
        if (!payload.notes) delete payload.notes;

        const res = await observationsAPI.create(payload);
        card.doneToday = true;
        card.todayObs = res.data;
      } catch (e) {
        const detail = e.response?.data?.detail;
        card.error = typeof detail === "string" ? detail : "Failed to save. Please try again.";
      } finally {
        card.saving = false;
      }
    };

    const reopen = (card) => {
      // Pre-fill form from existing observation so edits are additive
      const obs = card.todayObs;
      if (obs) {
        card.form = {
          treatment_id: card.treatmentId,
          observation_date: TODAY,
          treatments_completed: obs.treatments_completed ?? true,
          dead_fish_count: obs.dead_fish_count ?? 0,
          condition_trend: obs.condition_trend ?? "same",
          symptoms_lethargy: obs.symptoms_lethargy ?? false,
          symptoms_loss_of_appetite: obs.symptoms_loss_of_appetite ?? false,
          symptoms_spots: obs.symptoms_spots ?? false,
          symptoms_fin_damage: obs.symptoms_fin_damage ?? false,
          symptoms_breathing_issues: obs.symptoms_breathing_issues ?? false,
          notes: obs.notes ?? "",
        };
      }
      card.doneToday = false;
    };

    const trendLabel = (v) => {
      return { progress: "Improving", same: "Same", regress: "Worse" }[v] || v;
    };

    onMounted(load);

    return {
      loading, cards, todayLabel, doneCount,
      symptoms: SYMPTOMS, trendOptions: TREND_OPTIONS,
      save, reopen, trendLabel,
    };
  }
};
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.25rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.page-header h2 {
  margin: 0 0 0.2rem 0;
  font-size: 1.4rem;
  color: #1e3a5f;
}

.today-label {
  margin: 0;
  font-size: 0.85rem;
  color: #6b7280;
}

.summary-badges {
  display: flex;
  gap: 0.4rem;
  align-items: center;
  flex-wrap: wrap;
}

.badge {
  font-size: 0.78rem;
  font-weight: 600;
  padding: 0.25rem 0.65rem;
  border-radius: 9999px;
}

.badge-total { background: #e5e7eb; color: #374151; }
.badge-done  { background: #dbeafe; color: #1d4ed8; }
.badge-all-done { background: #d1fae5; color: #065f46; }

/* Cards */
.round-card {
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 2px 6px rgba(0,0,0,0.08);
  padding: 1.25rem;
  margin-bottom: 1rem;
  border-left: 4px solid #0ea5e9;
  transition: border-color 0.2s;
}

.round-card.done {
  border-left-color: #10b981;
}

/* Card top */
.card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.fish-info {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.fish-info h3 {
  margin: 0;
  font-size: 1.05rem;
  color: #111827;
}

.aquarium-badge {
  display: inline-block;
  background: #eff6ff;
  color: #1d4ed8;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.15rem 0.5rem;
  border-radius: 0.3rem;
  width: fit-content;
}

.sci {
  font-size: 0.78rem;
  color: #6b7280;
  font-style: italic;
}

.card-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.3rem;
}

.day-counter {
  font-size: 0.85rem;
  font-weight: 700;
  color: #0284c7;
  white-space: nowrap;
}

.day-counter.overdue {
  color: #dc2626;
}

.done-badge {
  font-size: 0.78rem;
  font-weight: 700;
  color: #059669;
  white-space: nowrap;
}

/* Protocols */
.protocols-line {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem;
  margin-bottom: 0.9rem;
  font-size: 0.8rem;
}

.protocols-label {
  color: #6b7280;
}

.proto-tag {
  background: #fef3c7;
  color: #92400e;
  font-size: 0.78rem;
  padding: 0.15rem 0.5rem;
  border-radius: 0.3rem;
  font-weight: 500;
}

/* Done summary */
.done-summary {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 0.5rem;
  padding: 0.75rem 1rem;
}

.done-row {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: center;
  font-size: 0.9rem;
  color: #374151;
}

.red { color: #dc2626; }

.trend-chip {
  font-size: 0.78rem;
  font-weight: 700;
  padding: 0.2rem 0.6rem;
  border-radius: 9999px;
}
.trend-chip.progress { background: #d1fae5; color: #065f46; }
.trend-chip.same     { background: #e5e7eb; color: #374151; }
.trend-chip.regress  { background: #fee2e2; color: #991b1b; }

.obs-notes {
  margin: 0.5rem 0 0.5rem 0;
  font-size: 0.85rem;
  color: #6b7280;
  font-style: italic;
}

.btn-edit {
  background: none;
  border: 1px solid #9ca3af;
  border-radius: 0.4rem;
  font-size: 0.8rem;
  padding: 0.25rem 0.65rem;
  cursor: pointer;
  color: #374151;
  margin-top: 0.5rem;
}

.btn-edit:hover { background: #f3f4f6; }

/* Form */
.obs-form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.dose-check {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  color: #111827;
}

.dose-check input[type="checkbox"] {
  width: 1.1rem;
  height: 1.1rem;
  accent-color: #0ea5e9;
}

.field-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.field-label {
  font-size: 0.85rem;
  color: #374151;
  min-width: 110px;
}

.count-input {
  width: 80px;
  padding: 0.35rem 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.4rem;
  font-size: 0.95rem;
  text-align: center;
}

/* Trend buttons */
.trend-buttons {
  display: flex;
  gap: 0.4rem;
}

.trend-btn {
  padding: 0.3rem 0.8rem;
  border-radius: 0.4rem;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.15s;
}

.trend-btn.progress        { background: #f0fdf4; color: #059669; border-color: #a7f3d0; }
.trend-btn.progress.active { background: #059669; color: white; border-color: #059669; }

.trend-btn.same            { background: #f9fafb; color: #374151; border-color: #d1d5db; }
.trend-btn.same.active     { background: #374151; color: white; border-color: #374151; }

.trend-btn.regress         { background: #fff7ed; color: #c2410c; border-color: #fed7aa; }
.trend-btn.regress.active  { background: #c2410c; color: white; border-color: #c2410c; }

/* Symptoms */
.symptoms-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.sym-check {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.82rem;
  color: #374151;
  cursor: pointer;
  background: #f3f4f6;
  padding: 0.25rem 0.6rem;
  border-radius: 0.35rem;
}

.sym-check input { accent-color: #0ea5e9; }

/* Notes */
.notes-input {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.4rem;
  font-size: 0.9rem;
  resize: vertical;
  box-sizing: border-box;
  font-family: inherit;
}

.notes-input:focus { outline: none; border-color: #0ea5e9; }

/* Save button */
.form-actions {
  display: flex;
  justify-content: flex-end;
}

.btn-save {
  padding: 0.6rem 1.5rem;
  background: #0ea5e9;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
}

.btn-save:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-save:hover:not(:disabled) { background: #0284c7; }

.error-msg {
  color: #dc2626;
  font-size: 0.85rem;
  margin: 0;
}

/* Empty / loading */
.loading, .empty-state {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
}

.btn-link {
  display: inline-block;
  margin-top: 0.75rem;
  color: #0ea5e9;
  text-decoration: underline;
  cursor: pointer;
}
</style>
