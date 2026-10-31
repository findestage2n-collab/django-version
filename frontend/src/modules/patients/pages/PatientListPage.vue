<script setup lang="ts">
import { useAuthStore } from "@/core/auth/auth.store";
import AppAlert from "@/shared/components/AppAlert.vue";
import AppPagination from "@/shared/components/AppPagination.vue";

import PatientTable from "../components/PatientTable.vue";
import { PAGE_SIZE, usePatientList } from "../composables/usePatientList";

const auth = useAuthStore();
const { items, count, page, search, loading, error } = usePatientList();
</script>

<template>
  <section class="space-y-4">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-semibold">{{ $t("patients.title") }}</h1>
      <RouterLink
        v-if="auth.can('patients.add_patient')"
        :to="{ name: 'patient-create' }"
        class="rounded-md bg-sky-700 px-4 py-2 text-sm font-medium text-white hover:bg-sky-800"
      >
        {{ $t("patients.new") }}
      </RouterLink>
    </div>
    <input
      v-model="search"
      type="search"
      :placeholder="$t('common.search')"
      class="w-full max-w-md rounded-md border border-slate-300 px-3 py-2 text-sm"
    />
    <AppAlert v-if="error">{{ error }}</AppAlert>
    <p v-if="loading" class="text-sm text-slate-500">{{ $t("app.loading") }}</p>
    <PatientTable :items="items" />
    <AppPagination :page="page" :count="count" :page-size="PAGE_SIZE" @change="page = $event" />
  </section>
</template>
