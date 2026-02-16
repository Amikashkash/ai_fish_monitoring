<template>
  <div class="supplier-scores">
    <h2>Supplier Performance</h2>
    <div v-if="suppliers.length > 0">
      <div v-for="supplier in suppliers" :key="supplier.source_country" class="supplier-card">
        <h3>{{ supplier.source_country }}</h3>
        <div class="score-badge" :class="`risk-${supplier.risk_level}`">
          {{ supplier.overall_score }}/100
        </div>
        <p><strong>Success Rate:</strong> {{ supplier.average_success_rate }}%</p>
        <p><strong>Total Shipments:</strong> {{ supplier.total_shipments }}</p>
        <div v-if="supplier.best_performing_species.length > 0">
          <h4>Best Species:</h4>
          <ul>
            <li v-for="species in supplier.best_performing_species" :key="species">
              {{ species }}
            </li>
          </ul>
        </div>
      </div>
    </div>
    <div v-else class="empty-state">
      <p>No supplier data available yet</p>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";
import { suppliersAPI } from "../api/client";

export default {
  name: "SupplierScores",
  setup() {
    const suppliers = ref([]);

    const loadScores = async () => {
      try {
        const res = await suppliersAPI.getScores();
        suppliers.value = res.data;
      } catch (error) {
        console.error("Failed to load supplier scores:", error);
      }
    };

    onMounted(loadScores);

    return { suppliers };
  }
};
</script>

<style scoped>
.supplier-card {
  background: white;
  padding: 1.5rem;
  margin: 1rem 0;
  border-radius: 0.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.score-badge {
  display: inline-block;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-weight: bold;
  margin: 0.5rem 0;
}

.risk-low {
  background: #10b981;
  color: white;
}

.risk-medium {
  background: #f59e0b;
  color: white;
}

.risk-high {
  background: #ef4444;
  color: white;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
}
</style>
