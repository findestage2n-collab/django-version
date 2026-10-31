<script setup lang="ts">
import { reactive } from "vue";

import AppButton from "@/shared/components/AppButton.vue";
import AppInput from "@/shared/components/AppInput.vue";

import type { Patient, PatientInput } from "../types";

const props = defineProps<{
  initial?: Patient;
  errors?: Record<string, string>;
  loading?: boolean;
}>();
const emit = defineEmits<{ submit: [input: PatientInput]; cancel: [] }>();

const form = reactive({
  nom: props.initial?.nom ?? "",
  prenom: props.initial?.prenom ?? "",
  sexe: props.initial?.sexe ?? "F",
  date_naissance: props.initial?.date_naissance ?? "",
  telephone: props.initial?.telephone ?? "",
  email: props.initial?.email ?? "",
  adresse: props.initial?.adresse ?? "",
});

function onSubmit() {
  emit("submit", {
    nom: form.nom.trim(),
    prenom: form.prenom.trim(),
    sexe: form.sexe as PatientInput["sexe"],
    // date vide -> null (champ optionnel côté API)
    date_naissance: form.date_naissance || null,
    telephone: form.telephone.trim(),
    email: form.email.trim(),
    adresse: form.adresse.trim(),
  });
}
</script>

<template>
  <form class="grid max-w-2xl gap-4 sm:grid-cols-2" @submit.prevent="onSubmit">
    <AppInput v-model="form.nom" :label="$t('patients.nom')" :error="errors?.nom" required />
    <AppInput v-model="form.prenom" :label="$t('patients.prenom')" :error="errors?.prenom" required />
    <label class="block text-sm">
      <span class="mb-1 block font-medium text-slate-700">{{ $t("patients.sexe") }}</span>
      <select v-model="form.sexe" class="w-full rounded-md border border-slate-300 px-3 py-2">
        <option value="F">{{ $t("patients.female") }}</option>
        <option value="M">{{ $t("patients.male") }}</option>
      </select>
    </label>
    <AppInput v-model="form.date_naissance" type="date" :label="$t('patients.dateNaissance')" :error="errors?.date_naissance" />
    <AppInput v-model="form.telephone" :label="$t('patients.telephone')" :error="errors?.telephone" />
    <AppInput v-model="form.email" type="email" :label="$t('patients.email')" :error="errors?.email" />
    <div class="sm:col-span-2">
      <AppInput v-model="form.adresse" :label="$t('patients.adresse')" :error="errors?.adresse" />
    </div>
    <div class="flex gap-3 sm:col-span-2">
      <AppButton type="submit" :loading="loading">{{ $t("common.save") }}</AppButton>
      <AppButton variant="secondary" @click="emit('cancel')">{{ $t("common.cancel") }}</AppButton>
    </div>
  </form>
</template>
