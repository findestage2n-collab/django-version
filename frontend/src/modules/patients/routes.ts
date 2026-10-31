import type { RouteRecordRaw } from "vue-router";

const routes: RouteRecordRaw[] = [
  {
    path: "patients",
    name: "patients",
    component: () => import("./pages/PatientListPage.vue"),
    meta: { permission: "patients.view_patient" },
  },
  {
    path: "patients/new",
    name: "patient-create",
    component: () => import("./pages/PatientFormPage.vue"),
    meta: { permission: "patients.add_patient" },
  },
  {
    path: "patients/:id",
    name: "patient-detail",
    component: () => import("./pages/PatientDetailPage.vue"),
    meta: { permission: "patients.view_patient" },
  },
  {
    path: "patients/:id/edit",
    name: "patient-edit",
    component: () => import("./pages/PatientFormPage.vue"),
    meta: { permission: "patients.change_patient" },
  },
];
export default routes;
