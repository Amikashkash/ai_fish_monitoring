import { createRouter, createWebHistory } from "vue-router";
import Dashboard from "./views/Dashboard.vue";
import ShipmentForm from "./views/ShipmentForm.vue";
import TreatmentView from "./views/TreatmentView.vue";
import DailyChecklist from "./views/DailyChecklist.vue";
import SupplierScores from "./views/SupplierScores.vue";

const routes = [
  {
    path: "/",
    name: "Dashboard",
    component: Dashboard
  },
  {
    path: "/shipments",
    name: "Shipments",
    component: ShipmentForm
  },
  {
    path: "/treatments",
    name: "Treatments",
    component: TreatmentView
  },
  {
    path: "/checklist/:treatmentId",
    name: "DailyChecklist",
    component: DailyChecklist,
    props: true
  },
  {
    path: "/suppliers",
    name: "Suppliers",
    component: SupplierScores
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
