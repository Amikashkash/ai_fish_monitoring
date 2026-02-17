import { createRouter, createWebHistory } from "vue-router";
import Dashboard from "./views/Dashboard.vue";
import ShipmentForm from "./views/ShipmentForm.vue";
import ShipmentsList from "./views/ShipmentsList.vue";
import TreatmentView from "./views/TreatmentView.vue";
import DailyChecklist from "./views/DailyChecklist.vue";
import DailyRounds from "./views/DailyRounds.vue";
import SupplierScores from "./views/SupplierScores.vue";
import DrugProtocols from "./views/DrugProtocols.vue";
import ExcelImport from "./views/ExcelImport.vue";

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
    path: "/shipments-list",
    name: "ShipmentsList",
    component: ShipmentsList
  },
  {
    path: "/import",
    name: "ExcelImport",
    component: ExcelImport
  },
  {
    path: "/treatments",
    name: "Treatments",
    component: TreatmentView
  },
  {
    path: "/daily",
    name: "DailyRounds",
    component: DailyRounds
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
  },
  {
    path: "/protocols",
    name: "Protocols",
    component: DrugProtocols
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
