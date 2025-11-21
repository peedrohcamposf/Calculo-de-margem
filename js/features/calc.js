import { parseBrazilNumber, formatBrazilNumber, safeDiv } from "../utils/numbers.js";
import { parcelas, maquinas } from "../core/state.js";

export function computeAll() {
  // parcelas
  parcelas.forEach(p => {
    const iEl = document.getElementById(`parcela_I_${p.row}`);
    const lEl = document.getElementById(`parcela_L_${p.row}`);
    const qEl = document.getElementById(`parcela_Q_${p.row}`);
    const jEl = document.getElementById(`parcela_J_${p.row}`);
    const nEl = document.getElementById(`parcela_N_${p.row}`);
    const oEl = document.getElementById(`parcela_O_${p.row}`);

    const iVal = parseBrazilNumber(iEl?.value);
    const lVal = parseBrazilNumber(lEl?.value);
    const qVal = parseBrazilNumber(qEl?.value);

    const jVal = iVal + lVal;
    const nVal = qVal * 2;
    const oVal = safeDiv(jVal, qVal);

    if (jEl) jEl.value = formatBrazilNumber(jVal);
    if (nEl) nEl.value = formatBrazilNumber(nVal);
    if (oEl) oEl.value = formatBrazilNumber(oVal);
  });

  // máquinas
  maquinas.forEach((_, idx) => {
    const row = idx + 1;

    const iEl = document.getElementById(`maq_I_${row}`);
    const lEl = document.getElementById(`maq_L_${row}`);
    const jEl = document.getElementById(`maq_J_${row}`);
    const nEl = document.getElementById(`maq_N_${row}`);
    const oEl = document.getElementById(`maq_O_${row}`);

    const iVal = parseBrazilNumber(iEl?.value);
    const lVal = parseBrazilNumber(lEl?.value);

    const jVal = iVal - lVal;
    const nVal = safeDiv(iVal, (lVal || 1));

    if (jEl) jEl.value = formatBrazilNumber(jVal);
    if (nEl) nEl.value = formatBrazilNumber(nVal);
    if (oEl) oEl.value = "";
  });
}
