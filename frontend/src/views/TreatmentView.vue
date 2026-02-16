<template>
  <div class="treatment-view">
    <h2>Active Treatments</h2>
    <div v-if="treatments.length > 0">
      <div v-for="treatment in treatments" :key="treatment.id" class="treatment-card">
        <h3>Treatment #{{ treatment.id }}</h3>
        <p><strong>Start Date:</strong> {{ treatment.start_date }}</p>
        <p><strong>Status:</strong> {{ treatment.status }}</p>
        <router-link :to="`/checklist/${treatment.id}`" class="btn btn-primary">
          Record Daily Observation
        </router-link>
      </div>
    </div>
    <div v-else class="empty-state">
      <p>No active treatments</p>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";
import { treatmentsAPI } from "../api/client";

export default {
  name: "TreatmentView",
  setup() {
    const treatments = ref([]);

    const loadTreatments = async () => {
      try {
        const res = await treatmentsAPI.list(true);
        treatments.value = res.data;
      } catch (error) {
        console.error("Failed to load treatments:", error);
      }
    };

    onMounted(loadTreatments);

    return { treatments };
  }
};
</script>

<style scoped>
.treatment-card {
  background: white;
  padding: 1.5rem;
  margin: 1rem 0;
  border-radius: 0.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.btn {
  display: inline-block;
  margin-top: 1rem;
  padding: 0.75rem 1.5rem;
  background: #0ea5e9;
  color: white;
  text-decoration: none;
  border-radius: 0.5rem;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
}
</style>
