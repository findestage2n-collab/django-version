import { createRouter, createWebHistory, type RouteRecordRaw } from "vue-router";

import AuthLayout from "@/app/layouts/AuthLayout.vue";
import MainLayout from "@/app/layouts/MainLayout.vue";
import { installAuthGuard } from "@/core/auth/guards";

// Chaque module déclare ses routes dans modules/<nom>/routes.ts : le routeur central
// ne change pas quand on ajoute un module (principe ouvert/fermé).
const moduleFiles = import.meta.glob<{ default: RouteRecordRaw[] }>("../../modules/*/routes.ts", {
  eager: true,
});
const moduleRoutes = Object.values(moduleFiles).flatMap((file) => file.default);

const publicRoutes = moduleRoutes.filter((route) => route.meta?.public);
const privateRoutes = moduleRoutes.filter((route) => !route.meta?.public);

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", component: MainLayout, children: privateRoutes },
    { path: "/", component: AuthLayout, children: publicRoutes },
    { path: "/:pathMatch(.*)*", redirect: { name: "dashboard" } },
  ],
});

installAuthGuard(router);
