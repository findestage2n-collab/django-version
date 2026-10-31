<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { ApiError, toApiError } from "@/core/api/errors";
import AppAlert from "@/shared/components/AppAlert.vue";

import { patientsApi } from "../api/patients.api";
import PatientForm from "../components/PatientForm.vue";
import type { Patient, PatientInput } from "../types";

const route = useRoute();
const router = useRouter();
const id = typeof route.params.id === "string" ? route.params.id : undefined;

const patient = ref<Patient>();
const loaded = ref(!id);
const saving = ref(false);
const fieldErrors = ref<Record<string, string>>({});
const message = ref("");

onMounted(async () => {
  if (!id) return;
  try {
    patient.value = await patientsApi.get(id);
  } catch (e) {
    message.value = toApiError(e).message;
  } finally {
    loaded.value = true;
  }
});

async function save(input: PatientInput, allowDuplicate = false) {
  saving.value = true;
  fieldErrors.value = {};
  message.value = "";
  try {
    const saved = id
      ? await patientsApi.update(id, input)
      : await patientsApi.create({ ...input, allow_duplicate: allowDuplicate });
    await router.push({ name: "patient-detail", params: { id: saved.public_id } });
  } catch (e) {
    const error = toApiError(e);
    if (error.code === "duplicate_patient" && window.confirm(`${error.message}\n`)) {
      return save(input, true);
    }
    fieldErrors.value = error.fieldErrors();
    message.value = error.message;
  } finally {
    saving.value = false;
  }
}
</script>

<template>
  <section class="space-y-4">
    <h1 class="text-2xl font-semibold">{{ id ? $t("common.edit") : $t("patients.new") }}</h1>
    <AppAlert v-if="message">{{ message }}</AppAlert>
    <PatientForm
      v-if="loaded"
      :initial="patient"
      :errors="fieldErrors"
      :loading="saving"
      @submit="save($event)"
      @cancel="router.back()"
    />
  </section>
</template>
