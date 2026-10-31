<script setup lang="ts">
import { formatDate } from "@/shared/utils/format";

import type { PatientListItem } from "../types";

defineProps<{ items: PatientListItem[] }>();
</script>

<template>
  <table class="w-full overflow-hidden rounded-lg bg-white text-left text-sm shadow-sm">
    <thead class="bg-slate-100 text-slate-600">
      <tr>
        <th class="px-4 py-2">{{ $t("patients.numero") }}</th>
        <th class="px-4 py-2">{{ $t("patients.nom") }}</th>
        <th class="px-4 py-2">{{ $t("patients.prenom") }}</th>
        <th class="px-4 py-2">{{ $t("patients.dateNaissance") }}</th>
        <th class="px-4 py-2">{{ $t("patients.telephone") }}</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="p in items" :key="p.public_id" class="border-t hover:bg-slate-50">
        <td class="px-4 py-2 font-mono">
          <RouterLink :to="{ name: 'patient-detail', params: { id: p.public_id } }" class="text-sky-700 hover:underline">
            {{ p.numero_dossier }}
          </RouterLink>
        </td>
        <td class="px-4 py-2">{{ p.nom }}</td>
        <td class="px-4 py-2">{{ p.prenom }}</td>
        <td class="px-4 py-2">{{ formatDate(p.date_naissance) }}</td>
        <td class="px-4 py-2">{{ p.telephone || "-" }}</td>
      </tr>
      <tr v-if="items.length === 0">
        <td colspan="5" class="px-4 py-6 text-center text-slate-500">{{ $t("common.empty") }}</td>
      </tr>
    </tbody>
  </table>
</template>
