// js/core/formatting.js
import { parseBrazilNumber, formatBrazilNumber } from "../utils/numbers.js";

/**
 * Formatação:
 * - Apenas campos com class "numeric" são manipulados.
 * - Durante digitação: NÃO formatar (para não mover cursor).
 * - No focus: remove sufixos "R$" e "%" e apresenta valor cru.
 * - No blur: aplica formatação final conforme data-type:
 *     data-type="money"  -> "1.234,56 R$"
 *     data-type="percent"-> "12,50%"
 *     data-type="int"    -> "123"
 * - Campos que não possuem data-type são tratados como simples números (sem sufixo).
 */

function toEditString(n) {
  // exibe com vírgula no foco para edição (ex: "1234,56")
  return String(n).replace(".", ",");
}

export function attachFormatting() {
  const nodes = Array.from(document.querySelectorAll(".numeric"));

  nodes.forEach(el => {
    // cleanup handlers if already attached
    if (el._formatFocus) el.removeEventListener("focus", el._formatFocus);
    if (el._formatBlur) el.removeEventListener("blur", el._formatBlur);

    el._formatFocus = (e) => {
      let v = String(e.target.value || "").trim();
      v = v.replace(/\s?R\$\s?/g, "").replace(/\s?%\s?/g, "");
      const n = parseBrazilNumber(v);
      if (e.target.dataset.type === "int") {
        e.target.value = (n ? String(Math.round(n)) : "");
      } else {
        e.target.value = (n ? toEditString(n) : "");
      }
    };

    el._formatBlur = (e) => {
      let v = String(e.target.value || "").trim();
      v = v.replace(/\s?R\$\s?/g, "").replace(/\s?%\s?/g, "");

      // integers: empty if none
      if (e.target.dataset.type === "int") {
        const n = parseInt(v);
        e.target.value = isNaN(n) ? "" : String(Math.round(n));
        return;
      }

      const n = parseBrazilNumber(v);
      if (!n) {
        // option chosen: keep empty (user requested "empty while nothing typed")
        e.target.value = "";
        return;
      }

      if (e.target.dataset.type === "money") {
        e.target.value = formatBrazilNumber(n) + " R$";
      } else if (e.target.dataset.type === "percent") {
        e.target.value = formatBrazilNumber(n) + "%";
      } else {
        e.target.value = formatBrazilNumber(n);
      }
    };

    el.addEventListener("focus", el._formatFocus);
    el.addEventListener("blur", el._formatBlur);
  });
}
