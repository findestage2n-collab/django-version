import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import { createI18n } from "vue-i18n";

import fr from "@/core/i18n/locales/fr.json";

import PatientForm from "./PatientForm.vue";

const i18n = createI18n({ legacy: false, locale: "fr", messages: { fr } });

describe("PatientForm", () => {
  it("émet les données saisies, sans espaces superflus", async () => {
    const wrapper = mount(PatientForm, { global: { plugins: [i18n] } });
    const inputs = wrapper.findAll("input");
    await inputs[0]!.setValue("  Mbarga ");
    await inputs[1]!.setValue("Alice");
    await wrapper.find("form").trigger("submit");
    const [payload] = wrapper.emitted("submit")![0] as [Record<string, unknown>];
    expect(payload).toMatchObject({ nom: "Mbarga", prenom: "Alice", date_naissance: null });
  });

  it("affiche les erreurs de validation renvoyées par l'API", () => {
    const wrapper = mount(PatientForm, {
      props: { errors: { nom: "Ce champ est obligatoire." } },
      global: { plugins: [i18n] },
    });
    expect(wrapper.text()).toContain("Ce champ est obligatoire.");
  });
});
