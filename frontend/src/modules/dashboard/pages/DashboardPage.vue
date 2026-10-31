<script setup lang="ts">
import { useAuthStore } from "@/core/auth/auth.store";

const auth = useAuthStore();
</script>

<template>
  <section>
    <h1 class="text-2xl font-semibold">{{ $t("nav.dashboard") }}</h1>
    <p class="mt-2 text-slate-600">Rôle(s) : {{ auth.user?.roles.join(", ") || "-" }}</p>
  </section>
</template>
