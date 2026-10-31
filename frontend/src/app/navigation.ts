export interface NavItem {
  label: string; // clé i18n
  to: string;
  permission?: string; // le lien n'est affiché que si l'utilisateur a ce droit
}

/** Ajouter un module = ajouter une entrée ici (et son routes.ts dans modules/<nom>/). */
export const navigation: NavItem[] = [
  { label: "nav.dashboard", to: "/" },
  { label: "nav.patients", to: "/patients", permission: "patients.view_patient" },
];
