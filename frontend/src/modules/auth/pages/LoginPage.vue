<script setup lang="ts">
import { ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { ApiError } from "@/core/api/errors";
import { useAuthStore } from "@/core/auth/auth.store";
import AppAlert from "@/shared/components/AppAlert.vue";
import AppButton from "@/shared/components/AppButton.vue";
import AppInput from "@/shared/components/AppInput.vue";

const auth = useAuthStore();
const router = useRouter();
const route = useRoute();

const username = ref("");
const password = ref("");
const loading = ref(false);
const errorKey = ref<string | null>(null);
const errorText = ref("");

async function submit() {
  loading.value = true;
  errorKey.value = null;
  try {
    await auth.login(username.value, password.value);
    const redirect = typeof route.query.redirect === "string" ? route.query.redirect : "/";
    await router.push(redirect);
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) errorKey.value = "auth.invalid";
    else errorText.value = error instanceof ApiError ? error.message : String(error);
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <form class="space-y-4" @submit.prevent="submit">
    <h1 class="text-xl font-semibold">{{ $t("auth.title") }}</h1>
    <AppAlert v-if="errorKey || errorText">{{ errorKey ? $t(errorKey) : errorText }}</AppAlert>
    <AppInput v-model="username" :label="$t('auth.username')" autocomplete="username" required />
    <AppInput v-model="password" :label="$t('auth.password')" type="password" autocomplete="current-password" required />
    <AppButton type="submit" :loading="loading" class="w-full">{{ $t("auth.submit") }}</AppButton>
  </form>
</template>
