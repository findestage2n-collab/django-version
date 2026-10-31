<script setup lang="ts">
withDefaults(
  defineProps<{ variant?: "primary" | "secondary" | "danger"; type?: "button" | "submit"; loading?: boolean }>(),
  { variant: "primary", type: "button", loading: false },
);
</script>

<template>
  <button
    :type="type"
    :disabled="loading"
    class="inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium transition disabled:opacity-60"
    :class="{
      'bg-sky-700 text-white hover:bg-sky-800': variant === 'primary',
      'border border-slate-300 bg-white text-slate-700 hover:bg-slate-50': variant === 'secondary',
      'bg-red-600 text-white hover:bg-red-700': variant === 'danger',
    }"
  >
    <slot />
  </button>
</template>
