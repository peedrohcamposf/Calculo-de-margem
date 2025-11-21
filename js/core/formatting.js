import { parseBrazilNumber, formatBrazilNumber } from "../utils/numbers.js";

export function attachFormatting() {
  document.querySelectorAll(".numeric").forEach(el => {
    el.oninput = () => document.dispatchEvent(new Event("recompute"));

    if (el._blurHandler) el.removeEventListener("blur", el._blurHandler);
    if (el._focusHandler) el.removeEventListener("focus", el._focusHandler);

    el._blurHandler = (e) => {
      const n = parseBrazilNumber(e.target.value);
      e.target.value = n === 0 ? "" : formatBrazilNumber(n);
    };
    el._focusHandler = (e) => {
      const n = parseBrazilNumber(e.target.value);
      e.target.value = n === 0 ? "" : String(n).replace('.', ',');
    };

    el.addEventListener("blur", el._blurHandler);
    el.addEventListener("focus", el._focusHandler);
  });
}
