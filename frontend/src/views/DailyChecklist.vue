<template>
  <div class="daily-checklist">
    <div class="checklist-header">
      <div v-if="fishName" class="fish-title">
        <h2>{{ fishName }}</h2>
        <p v-if="scientificName && scientificName !== fishName" class="sci">{{ scientificName }}</p>
        <p class="meta">Treatment #{{ treatmentId }} · Day {{ dayNum }}</p>
      </div>
      <div v-else>
        <h2>Daily Observation</h2>
        <p class="meta">Treatment #{{ treatmentId }}</p>
      </div>
    </div>

    <form @submit.prevent="handleSubmit" class="obs-form">
      <div class="form-group">
        <label>Observation Date</label>
        <input v-model="form.observation_date" type="date" :max="TODAY" required />
      </div>

      <div class="form-group">
        <label>Overall Condition (1–5)</label>
        <input v-model.number="form.overall_condition_score" type="number" min="1" max="5" required />
      </div>

      <div class="form-group">
        <label>Symptoms</label>
        <div class="symptom-list">
          <label class="sym"><input type="checkbox" v-model="form.symptoms_lethargy" /> Lethargy</label>
          <label class="sym"><input type="checkbox" v-model="form.symptoms_loss_of_appetite" /> Loss of Appetite</label>
          <label class="sym"><input type="checkbox" v-model="form.symptoms_spots" /> Spots / Discoloration</label>
          <label class="sym"><input type="checkbox" v-model="form.symptoms_fin_damage" /> Fin Damage</label>
          <label class="sym"><input type="checkbox" v-model="form.symptoms_breathing_issues" /> Breathing Issues</label>
        </div>
        <input v-model="form.symptoms_other" type="text" class="other-symptoms" placeholder="Other symptoms (optional)" />
      </div>

      <div class="form-group">
        <label class="dose-label">
          <input type="checkbox" v-model="form.treatments_completed" />
          Treatments completed today
        </label>
      </div>

      <div class="form-group">
        <label>Notes (optional)</label>
        <textarea v-model="form.notes" rows="3" placeholder="Observations, changes, concerns..."></textarea>
      </div>

      <button type="submit" class="btn-save" :disabled="submitting">
        {{ submitting ? "Saving..." : "Save Observation" }}
      </button>
      <p v-if="error" class="error-msg">{{ error }}</p>
    </form>
  </div>
</template>

<script>
import { ref, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import { observationsAPI, treatmentsAPI, shipmentsAPI } from "../api/client";

export default {
  name: "DailyChecklist",
  props: ["treatmentId"],
  setup(props) {
    const router = useRouter();
    const submitting = ref(false);
    const error = ref("");
    const fishName = ref("");
    const scientificName = ref("");
    const startDate = ref(null);

    const TODAY = new Date().toISOString().split("T")[0];

    const form = ref({
      treatment_id: parseInt(props.treatmentId),
      observation_date: TODAY,
      overall_condition_score: 3,
      symptoms_lethargy: false,
      symptoms_loss_of_appetite: false,
      symptoms_spots: false,
      symptoms_fin_damage: false,
      symptoms_breathing_issues: false,
      treatments_completed: true,
      symptoms_other: "",
      notes: ""
    });

    const dayNum = computed(() => {
      if (!startDate.value || !form.value.observation_date) return "?";
      const start = new Date(startDate.value);
      const obs = new Date(form.value.observation_date);
      return Math.max(1, Math.floor((obs - start) / 86400000) + 1);
    });

    onMounted(async () => {
      try {
        const tRes = await treatmentsAPI.getById(parseInt(props.treatmentId));
        const t = tRes.data;
        startDate.value = t.start_date;
        const sRes = await shipmentsAPI.getById(t.shipment_id);
        const s = sRes.data;
        fishName.value = s.common_name || s.scientific_name;
        scientificName.value = s.scientific_name;
      } catch {
        // Non-critical — form still works without fish name
      }
    });

    const handleSubmit = async () => {
      submitting.value = true;
      error.value = "";
      try {
        await observationsAPI.create(form.value);
        router.push("/treatments");
      } catch (e) {
        error.value = e.response?.data?.detail || "Failed to save observation.";
      } finally {
        submitting.value = false;
      }
    };

    return { form, submitting, error, fishName, scientificName, dayNum, TODAY };
  }
};
</script>

<style scoped>
.checklist-header {
  margin-bottom: 1.5rem;
}

.fish-title h2 {
  margin: 0 0 0.2rem 0;
  color: #1e3a5f;
}

.sci {
  margin: 0 0 0.2rem 0;
  font-style: italic;
  color: #6b7280;
  font-size: 0.9rem;
}

.meta {
  margin: 0;
  font-size: 0.8rem;
  color: #9ca3af;
}

.obs-form {
  background: white;
  border-radius: 0.75rem;
  padding: 1.5rem;
  box-shadow: 0 2px 6px rgba(0,0,0,0.08);
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-group label {
  display: block;
  font-size: 0.85rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.4rem;
}

.form-group input[type="date"],
.form-group input[type="number"],
.form-group textarea {
  width: 100%;
  padding: 0.6rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  font-size: 0.95rem;
  font-family: inherit;
  box-sizing: border-box;
}

.form-group input[type="date"]:focus,
.form-group input[type="number"]:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #0ea5e9;
}

.symptom-list {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.sym {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: #374151;
  cursor: pointer;
}

.other-symptoms {
  margin-top: 0.5rem;
  width: 100%;
  padding: 0.45rem 0.65rem;
  border: 1px solid #d1d5db;
  border-radius: 0.4rem;
  font-size: 0.9rem;
  box-sizing: border-box;
}

.dose-label {
  display: flex !important;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.btn-save {
  width: 100%;
  padding: 0.85rem;
  background: #0ea5e9;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  margin-top: 0.5rem;
}

.btn-save:hover:not(:disabled) { background: #0284c7; }
.btn-save:disabled { opacity: 0.6; cursor: not-allowed; }

.error-msg {
  color: #dc2626;
  font-size: 0.88rem;
  margin-top: 0.5rem;
}
</style>
