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
import LoginView from "./views/LoginView.vue";

// Write-only routes: redirect to /login if not admin
const ADMIN_ROUTES = ["/shipments", "/import", "/daily", "/checklist"];

const routes = [
  { path: "/", name: "Dashboard", component: Dashboard },
  { path: "/shipments", name: "Shipments", component: ShipmentForm, meta: { requiresAdmin: true } },
  { path: "/shipments-list", name: "ShipmentsList", component: ShipmentsList },
  { path: "/import", name: "ExcelImport", component: ExcelImport, meta: { requiresAdmin: true } },
  { path: "/treatments", name: "Treatments", component: TreatmentView },
  { path: "/daily", name: "DailyRounds", component: DailyRounds, meta: { requiresAdmin: true } },
  { path: "/checklist/:treatmentId", name: "DailyChecklist", component: DailyChecklist, props: true, meta: { requiresAdmin: true } },
  { path: "/suppliers", name: "Suppliers", component: SupplierScores },
  { path: "/protocols", name: "Protocols", component: DrugProtocols },
  { path: "/login", name: "Login", component: LoginView }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// Guard: write-only routes require admin JWT
router.beforeEach((to) => {
  if (!to.meta.requiresAdmin) return true;
  const token = localStorage.getItem("fm_admin_token");
  if (!token) return { path: "/login", query: { redirect: to.fullPath } };
  try {
    const { exp } = JSON.parse(atob(token.split(".")[1]));
    if (exp && exp < Date.now() / 1000) return { path: "/login", query: { redirect: to.fullPath } };
  } catch {
    return { path: "/login", query: { redirect: to.fullPath } };
  }
  return true;
});

export default router;
