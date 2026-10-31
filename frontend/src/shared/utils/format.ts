/** Dates reçues en ISO 8601 (UTC) ; affichage en français, fuseau local du navigateur. */
export function formatDate(value: string | null | undefined): string {
  if (!value) return "-";
  return new Intl.DateTimeFormat("fr-FR", { dateStyle: "medium" }).format(new Date(value));
}
