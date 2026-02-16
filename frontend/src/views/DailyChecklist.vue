<template>
  <div class="daily-checklist">
    <h2>Daily Observation</h2>
    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label>Overall Condition (1-5)</label>
        <input v-model.number="form.overall_condition_score" type="number" min="1" max="5" required />
      </div>

      <div class="form-group">
        <h3>Symptoms</h3>
        <label><input type="checkbox" v-model="form.symptoms_lethargy" /> Lethargy</label>
        <label><input type="checkbox" v-model="form.symptoms_loss_of_appetite" /> Loss of Appetite</label>
        <label><input type="checkbox" v-model="form.symptoms_spots" /> Spots/Discoloration</label>
        <label><input type="checkbox" v-model="form.symptoms_fin_damage" /> Fin Damage</label>
        <label><input type="checkbox" v-model="form.symptoms_breathing_issues" /> Breathing Issues</label>
      </div>

      <div class="form-group">
        <label>Treatments Completed Today?</label>
        <input type="checkbox" v-model="form.treatments_completed" />
      </div>

      <div class="form-group">
        <label>Notes (optional)</label>
        <textarea v-model="form.notes" rows="3"></textarea>
      </div>

      <button type="submit" class="btn btn-primary">Save Observation</button>
    </form>
  </div>
</template>

<script>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { observationsAPI } from "../api/client";

export default {
  name: "DailyChecklist",
  props: ["treatmentId"],
  setup(props) {
    const router = useRouter();
    const form = ref({
      treatment_id: parseInt(props.treatmentId),
      observation_date: new Date().toISOString().split("T")[0],
      overall_condition_score: 3,
      symptoms_lethargy: false,
      symptoms_loss_of_appetite: false,
      symptoms_spots: false,
      symptoms_fin_damage: false,
      symptoms_breathing_issues: false,
      treatments_completed: true,
      notes: ""
    });

    const handleSubmit = async () => {
      try {
        await observationsAPI.create(form.value);
        alert("Observation saved!");
        router.push("/treatments");
      } catch (error) {
        alert("Failed to save observation: " + error.message);
      }
    };

    return { form, handleSubmit };
  }
};
</script>

<style scoped>
.form-group {
  margin-bottom: 1.5rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
}

input[type="checkbox"] {
  margin-right: 0.5rem;
}

input,
textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
}

.btn-primary {
  width: 100%;
  padding: 1rem;
  background: #0ea5e9;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 1rem;
  cursor: pointer;
}
</style>
