<template>
  <div class="dashboard">
    <h2>Dashboard</h2>
    <div class="stats">
      <div class="stat-card">
        <h3>{{ activeTreatments.length }}</h3>
        <p>Active Treatments</p>
      </div>
      <div class="stat-card">
        <h3>{{ totalShipments }}</h3>
        <p>Total Shipments</p>
      </div>
    </div>

    <div class="actions">
      <router-link to="/shipments" class="btn btn-primary">
        Add New Shipment
      </router-link>
    </div>

    <div class="active-treatments" v-if="activeTreatments.length > 0">
      <h3>Active Treatments</h3>
      <div v-for="treatment in activeTreatments" :key="treatment.id" class="treatment-card">
        <h4>Treatment #{{ treatment.id }}</h4>
        <p>Start Date: {{ treatment.start_date }}</p>
        <router-link :to="`/checklist/${treatment.id}`" class="btn btn-small">
          Record Observation
        </router-link>
      </div>
    </div>

    <div v-else class="empty-state">
      <p>No active treatments. Create a shipment to get started!</p>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";
import { treatmentsAPI, shipmentsAPI } from "../api/client";

export default {
  name: "Dashboard",
  setup() {
    const activeTreatments = ref([]);
    const totalShipments = ref(0);

    const loadData = async () => {
      try {
        const treatmentsRes = await treatmentsAPI.list(true);
        activeTreatments.value = treatmentsRes.data;

        const shipmentsRes = await shipmentsAPI.list();
        totalShipments.value = shipmentsRes.data.total || 0;
      } catch (error) {
        console.error("Failed to load dashboard data:", error);
      }
    };

    onMounted(loadData);

    return { activeTreatments, totalShipments };
  }
};
</script>

<style scoped>
.dashboard {
  padding: 1rem 0;
}

.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin: 1rem 0;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 0.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  text-align: center;
}

.stat-card h3 {
  font-size: 2rem;
  color: #0ea5e9;
  margin-bottom: 0.5rem;
}

.actions {
  margin: 2rem 0;
}

.btn {
  display: inline-block;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-primary {
  background: #0ea5e9;
  color: white;
}

.btn-primary:hover {
  background: #0284c7;
}

.btn-small {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
}

.treatment-card {
  background: white;
  padding: 1rem;
  margin: 1rem 0;
  border-radius: 0.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
}
</style>
