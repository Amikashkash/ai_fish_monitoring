<template>
  <div class="shipment-form">
    <h2>New Shipment</h2>
    <p class="subtitle">Create a shipment record. After saving, open it in the Shipments list to add fish species.</p>
    <form @submit.prevent="handleSubmit">
      <div class="form-row">
        <div class="form-group">
          <label>Arrival Date</label>
          <input v-model="form.date" type="date" required />
        </div>
        <div class="form-group">
          <label>Source Country</label>
          <input v-model="form.source" placeholder="e.g. Thailand" />
        </div>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label>Supplier Name</label>
          <input v-model="form.supplier_name" placeholder="e.g. Aqua Fish Ltd" />
        </div>
        <div class="form-group">
          <label>Invoice Number</label>
          <input v-model="form.invoice_number" placeholder="INV-001" />
        </div>
      </div>

      <div class="form-group">
        <label>Notes</label>
        <input v-model="form.notes" placeholder="Optional notes" />
      </div>

      <p v-if="error" class="error-msg">{{ error }}</p>

      <div class="form-actions">
        <button type="submit" class="btn btn-primary" :disabled="saving">
          {{ saving ? 'Creating...' : 'Create Shipment' }}
        </button>
        <button type="button" class="btn btn-secondary" @click="$router.push('/shipments-list')">
          Cancel
        </button>
      </div>
    </form>
  </div>
</template>

<script>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { invoicesAPI } from "../api/client";

export default {
  name: "ShipmentForm",
  setup() {
    const router = useRouter();
    const saving = ref(false);
    const error = ref("");
    const form = ref({
      date: new Date().toISOString().split("T")[0],
      source: "",
      supplier_name: "",
      invoice_number: "",
      notes: ""
    });

    const handleSubmit = async () => {
      saving.value = true;
      error.value = "";
      try {
        await invoicesAPI.create(form.value);
        router.push("/shipments-list");
      } catch (e) {
        error.value = e.response?.data?.detail || "Failed to create shipment.";
      } finally {
        saving.value = false;
      }
    };

    return { form, saving, error, handleSubmit };
  }
};
</script>

<style scoped>
.shipment-form { max-width: 600px; margin: 0 auto; }
.shipment-form h2 { font-size: 1.5rem; color: #1e293b; margin-bottom: 0.25rem; }
.subtitle { color: #64748b; font-size: 0.9rem; margin-bottom: 1.5rem; }

.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem; }
.form-group { display: flex; flex-direction: column; margin-bottom: 1rem; }
.form-group label { display: block; margin-bottom: 0.4rem; font-weight: 600; font-size: 0.85rem; color: #374151; }
.form-group input { width: 100%; padding: 0.65rem 0.75rem; border: 1px solid #d1d5db; border-radius: 0.5rem; font-size: 0.95rem; box-sizing: border-box; }
.form-group input:focus { outline: none; border-color: #0ea5e9; }

.error-msg { color: #dc2626; font-size: 0.9rem; margin-bottom: 1rem; }

.form-actions { display: flex; gap: 1rem; margin-top: 1.5rem; }
.btn { flex: 1; padding: 0.75rem; border: none; border-radius: 0.5rem; font-weight: 600; cursor: pointer; font-size: 0.95rem; }
.btn-primary { background: #0ea5e9; color: white; }
.btn-primary:hover { background: #0284c7; }
.btn-primary:disabled { opacity: 0.6; cursor: default; }
.btn-secondary { background: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; }
.btn-secondary:hover { background: #e2e8f0; }
</style>
