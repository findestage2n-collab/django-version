<script setup lang="ts">
defineProps<{ tone?: "error" | "info" }>();
</script>

<template>
  <div
    role="alert"
    class="rounded-md border px-4 py-3 text-sm"
    :class="tone === 'info' ? 'border-sky-200 bg-sky-50 text-sky-800' : 'border-red-200 bg-red-50 text-red-800'"
  >
    <slot />
  </div>
</template>
