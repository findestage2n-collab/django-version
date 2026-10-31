import { onBeforeUnmount, ref, watch, type Ref } from "vue";

/** Valeur « retardée » : évite un appel API à chaque frappe. */
export function useDebounced<T>(source: Ref<T>, delayMs = 300): Ref<T> {
  const debounced = ref(source.value) as Ref<T>;
  let timer: ReturnType<typeof setTimeout> | undefined;
  watch(source, (value) => {
    clearTimeout(timer);
    timer = setTimeout(() => (debounced.value = value), delayMs);
  });
  onBeforeUnmount(() => clearTimeout(timer));
  return debounced;
}
