<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { toApiError } from "@/core/api/errors";
import { useAuthStore } from "@/core/auth/auth.store";
import AppAlert from "@/shared/components/AppAlert.vue";
import AppButton from "@/shared/components/AppButton.vue";
import { formatDate } from "@/shared/utils/format";

import { patientsApi } from "../api/patients.api";
import type { Patient } from "../types";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const id = String(route.params.id);

const patient = ref<Patient>();
const error = ref("");

onMounted(async () => {
  try {
    patient.value = await patientsApi.get(id);
  } catch (e) {
    error.value = toApiError(e).message;
  }
});

async function archive() {
  if (!window.confirm("Archiver ce dossier ?")) return;
  try {
    await patientsApi.archive(id);
    await router.push({ name: "patients" });
  } catch (e) {
    error.value = toApiError(e).message;
  }
}
</script>

<template>
  <section class="space-y-4">
    <AppAlert v-if="error">{{ error }}</AppAlert>
    <template v-if="patient">
      <div class="flex items-start justify-between">
        <div>
          <h1 class="text-2xl font-semibold">{{ patient.nom }} {{ patient.prenom }}</h1>
          <p class="font-mono text-sm text-slate-500">{{ patient.numero_dossier }}</p>
        </div>
        <div class="flex gap-2">
          <RouterLink
            v-if="auth.can('patients.change_patient')"
            :to="{ name: 'patient-edit', params: { id } }"
            class="rounded-md border border-slate-300 bg-white px-4 py-2 text-sm hover:bg-slate-50"
          >
            {{ $t("common.edit") }}
          </RouterLink>
          <AppButton v-if="auth.can('patients.delete_patient')" variant="danger" @click="archive">
            {{ $t("common.archive") }}
          </AppButton>
        </div>
      </div>
      <dl class="grid max-w-2xl grid-cols-2 gap-x-6 gap-y-3 rounded-lg bg-white p-6 text-sm shadow-sm">
        <dt class="text-slate-500">{{ $t("patients.dateNaissance") }}</dt>
        <dd>{{ formatDate(patient.date_naissance) }}<span v-if="patient.age != null"> ({{ patient.age }} ans)</span></dd>
        <dt class="text-slate-500">{{ $t("patients.telephone") }}</dt>
        <dd>{{ patient.telephone || "-" }}</dd>
        <dt class="text-slate-500">{{ $t("patients.email") }}</dt>
        <dd>{{ patient.email || "-" }}</dd>
        <dt class="text-slate-500">{{ $t("patients.adresse") }}</dt>
        <dd>{{ patient.adresse || "-" }}</dd>
      </dl>
    </template>
  </section>
</template>
