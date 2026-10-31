import { createPinia } from "pinia";
import { createApp } from "vue";

import App from "./App.vue";
import { router } from "./app/router";
import { setAuthFailureHandler } from "./core/api/http";
import { useAuthStore } from "./core/auth/auth.store";
import { i18n } from "./core/i18n";
import "./style.css";

const app = createApp(App);
const pinia = createPinia();
app.use(pinia).use(router).use(i18n);

// Session expirée et impossible à renouveler : retour à la connexion.
setAuthFailureHandler(() => {
  useAuthStore().reset();
  void router.push({ name: "login" });
});

app.mount("#app");
