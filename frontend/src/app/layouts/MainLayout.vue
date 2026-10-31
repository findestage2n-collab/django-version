<script setup lang="ts">
import { computed } from "vue";
import { useRouter } from "vue-router";

import { navigation } from "@/app/navigation";
import { useAuthStore } from "@/core/auth/auth.store";

const auth = useAuthStore();
const router = useRouter();
const items = computed(() => navigation.filter((i) => !i.permission || auth.can(i.permission)));

async function logout() {
  await auth.logout().catch(() => undefined);
  await router.push({ name: "login" });
}
</script>

<template>
  <div class="flex min-h-screen">
    <aside class="w-60 shrink-0 bg-slate-900 p-4 text-slate-100">
      <p class="mb-6 text-lg font-semibold">{{ $t("app.name") }}</p>
      <nav class="space-y-1">
        <RouterLink
          v-for="item in items"
          :key="item.to"
          :to="item.to"
          class="block rounded px-3 py-2 text-sm hover:bg-slate-800"
          active-class="bg-slate-800"
        >
          {{ $t(item.label) }}
        </RouterLink>
      </nav>
    </aside>
    <div class="flex min-w-0 flex-1 flex-col">
      <header class="flex items-center justify-between border-b bg-white px-6 py-3">
        <span class="text-sm text-slate-600">{{ auth.user?.first_name }} {{ auth.user?.last_name }} ({{ auth.user?.username }})</span>
        <button class="text-sm text-sky-700 hover:underline" @click="logout">{{ $t("app.logout") }}</button>
      </header>
      <main class="flex-1 p-6"><RouterView /></main>
    </div>
  </div>
</template>
