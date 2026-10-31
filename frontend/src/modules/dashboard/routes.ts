import type { RouteRecordRaw } from "vue-router";

const routes: RouteRecordRaw[] = [
  { path: "", name: "dashboard", component: () => import("./pages/DashboardPage.vue") },
];
export default routes;
