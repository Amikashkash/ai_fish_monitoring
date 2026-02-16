<template>
  <div class="shipment-form">
    <h2>Add New Shipment</h2>
    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label>Scientific Name</label>
        <input v-model="form.scientific_name" required />
      </div>

      <div class="form-group">
        <label>Common Name</label>
        <input v-model="form.common_name" required />
      </div>

      <div class="form-group">
        <label>Source Country</label>
        <select v-model="form.source" required>
          <option value="Sri Lanka">Sri Lanka</option>
          <option value="Thailand">Thailand</option>
          <option value="Singapore">Singapore</option>
          <option value="Malaysia">Malaysia</option>
          <option value="Indonesia">Indonesia</option>
        </select>
      </div>

      <div class="form-group">
        <label>Quantity</label>
        <input v-model.number="form.quantity" type="number" min="1" required />
      </div>

      <div class="form-group">
        <label>Aquarium Volume (Liters)</label>
        <input v-model.number="form.aquarium_volume_liters" type="number" min="1" required />
      </div>

      <div class="form-group">
        <label>Fish Size (optional)</label>
        <input v-model="form.fish_size" placeholder="e.g., small, medium, 3cm" />
      </div>

      <div v-if="recommendation" class="recommendation-box">
        <h3>AI Recommendation</h3>
        <p><strong>Confidence:</strong> {{ recommendation.confidence }}</p>
        <p v-if="recommendation.success_rate">
          <strong>Success Rate:</strong> {{ recommendation.success_rate }}%
        </p>
        <p>{{ recommendation.recommendation }}</p>
      </div>

      <div class="form-actions">
        <button type="button" @click="getRecommendation" class="btn btn-secondary">
          Get AI Advice
        </button>
        <button type="submit" class="btn btn-primary">
          Create Shipment
        </button>
      </div>
    </form>
  </div>
</template>

<script>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { shipmentsAPI, recommendationsAPI } from "../api/client";

export default {
  name: "ShipmentForm",
  setup() {
    const router = useRouter();
    const form = ref({
      scientific_name: "",
      common_name: "",
      source: "Thailand",
      quantity: 10,
      aquarium_volume_liters: 100,
      fish_size: "",
      date: new Date().toISOString().split("T")[0]
    });
    const recommendation = ref(null);

    const getRecommendation = async () => {
      try {
        const res = await recommendationsAPI.preShipment(
          form.value.scientific_name,
          form.value.source
        );
        recommendation.value = res.data;
      } catch (error) {
        alert("Failed to get recommendation: " + error.message);
      }
    };

    const handleSubmit = async () => {
      try {
        await shipmentsAPI.create(form.value);
        alert("Shipment created successfully!");
        router.push("/");
      } catch (error) {
        alert("Failed to create shipment: " + error.message);
      }
    };

    return { form, recommendation, getRecommendation, handleSubmit };
  }
};
</script>

<style scoped>
.shipment-form {
  max-width: 600px;
  margin: 0 auto;
}

.form-group {
  margin-bottom: 1rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

input,
select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  font-size: 1rem;
}

.recommendation-box {
  background: #f0f9ff;
  border: 1px solid #0ea5e9;
  padding: 1rem;
  border-radius: 0.5rem;
  margin: 1rem 0;
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
}

.btn {
  flex: 1;
  padding: 0.75rem;
  border: none;
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;
}

.btn-primary {
  background: #0ea5e9;
  color: white;
}

.btn-secondary {
  background: #6b7280;
  color: white;
}
</style>
