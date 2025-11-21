import { parseBrazilNumber, formatBrazilNumber, safeDiv } from "../utils/numbers.js";
import { parcelas, maquinas } from "../core/state.js";

/**
 * computeAll: faz cálculos seguros sem depender de ids que não existem.
 * - Para parcelas: calcula juros = valor * (jurosPercent/100)
 *   e VPL = valor - juros (exemplo simples). Ajuste conforme regra real.
 * - Para máquinas: atualmente não realiza cálculos complexos (preserva estabilidade).
 */
export function computeAll() {
  // === Parcelas ===
  const parcelaRows = Array.from(document.querySelectorAll("#parcelasList .cheader"));
  parcelaRows.forEach((rowEl, idx) => {
    // os inputs na ordem no renderParcelas são:
    // [0] label, [1] dias1 (readonly), [2] valor, [3] percentual, [4] dias2, [5] jurosPercent, [6] vpl, [7] juros
    const inputs = Array.from(rowEl.querySelectorAll(".col-header input"));
    if (inputs.length < 7) return;

    const valor = parseBrazilNumber(inputs[2]?.value) || 0;
    const jurosPercent = parseBrazilNumber(inputs[5]?.value) || 0;

    const juros = (valor * jurosPercent) / 100;
    const vpl = valor - juros;

    if (inputs[6]) inputs[6].value = formatBrazilNumber(vpl);
    if (inputs[7]) inputs[7].value = formatBrazilNumber(juros);
  });

  // === Máquinas ===
  // Não há IDs padronizados; para estabilidade apenas percorremos e evitamos exceptions.
  const maquinasRows = Array.from(document.querySelectorAll(".maquina-row"));
  maquinasRows.forEach((rowEl, idx) => {
    // Exemplo seguro: se houver campo de quantidade e valor, você pode calcular total
    try {
      const valorInput = rowEl.querySelector('input[data-field="Q"]');
      const quantInput = rowEl.querySelector('input[data-field="N"]');
      const totalEl = rowEl.querySelector('.inpValorCompra');

      const valor = parseBrazilNumber(valorInput?.value) || 0;
      const qtd = parseBrazilNumber(quantInput?.value) || 0;

      // exemplo: se quiser preencher valorCompra com valor * qtd:
      if (totalEl && !isNaN(valor) && !isNaN(qtd)) {
        totalEl.value = formatBrazilNumber(valor * qtd);
      }
    } catch (err) {
      // nunca lançar: manter computeAll resiliente
      // console.debug("computeAll (maquinas) safe-catch:", err);
    }
  });
}
