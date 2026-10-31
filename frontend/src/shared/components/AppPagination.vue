<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{ page: number; count: number; pageSize: number }>();
const emit = defineEmits<{ change: [page: number] }>();
const pages = computed(() => Math.max(1, Math.ceil(props.count / props.pageSize)));
</script>

<template>
  <nav class="flex items-center justify-between text-sm" aria-label="Pagination">
    <span class="text-slate-600">{{ count }} résultat(s) - page {{ page }} / {{ pages }}</span>
    <div class="flex gap-2">
      <button class="rounded border px-3 py-1 disabled:opacity-50" :disabled="page <= 1" @click="emit('change', page - 1)">
        {{ $t("common.previous") }}
      </button>
      <button class="rounded border px-3 py-1 disabled:opacity-50" :disabled="page >= pages" @click="emit('change', page + 1)">
        {{ $t("common.next") }}
      </button>
    </div>
  </nav>
</template>
