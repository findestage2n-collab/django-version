import { ref, watch } from "vue";

import { toApiError } from "@/core/api/errors";
import { useDebounced } from "@/shared/composables/useDebounced";

import { patientsApi } from "../api/patients.api";
import type { PatientListItem } from "../types";

export const PAGE_SIZE = 20;

/** État et chargement de la liste : recherche (anti-rebond) + pagination. */
export function usePatientList() {
  const items = ref<PatientListItem[]>([]);
  const count = ref(0);
  const page = ref(1);
  const search = ref("");
  const loading = ref(false);
  const error = ref("");
  const debouncedSearch = useDebounced(search);

  async function load() {
    loading.value = true;
    error.value = "";
    try {
      const result = await patientsApi.list({
        page: page.value,
        page_size: PAGE_SIZE,
        q: debouncedSearch.value || undefined,
      });
      items.value = result.results;
      count.value = result.count;
    } catch (e) {
      error.value = toApiError(e).message;
    } finally {
      loading.value = false;
    }
  }

  watch(debouncedSearch, () => {
    page.value = 1;
  });
  watch([page, debouncedSearch], load, { immediate: true });

  return { items, count, page, search, loading, error, reload: load };
}
