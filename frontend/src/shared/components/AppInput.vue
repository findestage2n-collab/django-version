<script setup lang="ts">
defineProps<{ label: string; type?: string; error?: string; required?: boolean; autocomplete?: string }>();
const model = defineModel<string | null>({ default: "" });
</script>

<template>
  <label class="block text-sm">
    <span class="mb-1 block font-medium text-slate-700">
      {{ label }}<span v-if="required" class="text-red-600"> *</span>
    </span>
    <input
      v-model="model"
      :type="type ?? 'text'"
      :required="required"
      :autocomplete="autocomplete"
      class="w-full rounded-md border px-3 py-2 focus:outline-none focus:ring-2 focus:ring-sky-600"
      :class="error ? 'border-red-500' : 'border-slate-300'"
    />
    <span v-if="error" class="mt-1 block text-xs text-red-600">{{ error }}</span>
  </label>
</template>
