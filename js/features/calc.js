// js/features/calc.js
import { parseBrazilNumber, formatBrazilNumber } from "../utils/numbers.js";

/* Sum all machines values: valorVenda * quantidade for every row */
function getTotalMachinesValue() {
  const rows = Array.from(document.querySelectorAll(".maquina-row"));
  let total = 0;
  rows.forEach(row => {
    const valEl = row.querySelector('input[data-field="Q"]');
    const qtdEl = row.querySelector('input[data-field="N"]');

    const valor = parseBrazilNumber(valEl?.value || "");
    const qtd = parseBrazilNumber(qtdEl?.value || "");
    total += (valor * qtd);
  });
  return total;
}

function fmtMoney(n) {
  return formatBrazilNumber(isNaN(n) ? 0 : n) + " R$";
}
function fmtPercent(n) {
  return formatBrazilNumber(isNaN(n) ? 0 : n) + "%";
}
function fmtInt(n) {
  return String(isNaN(n) ? 0 : Math.round(n));
}

export function computeAll() {
  const total = getTotalMachinesValue() || 0;

  const jurosRaw = document.getElementById("Juros_taxa")?.value || "";
  const jurosTaxa = (parseBrazilNumber(jurosRaw) || 0) / 100;

  const list = document.getElementById("parcelasList");
  if (!list) return;

  const rows = Array.from(list.querySelectorAll(".cheader"));
  if (!rows.length) return;

  const parcelaRows = rows.filter(r => r.dataset.row !== "0");
  const qtdParcelas = parcelaRows.length;

  const v0 = document.getElementById("parcela_valor_0");
  const p0 = document.getElementById("parcela_percentual_0");

  const rawVal = v0?.value.replace(/R\$|%/g, "").trim() || "";
  const rawPerc = p0?.value.replace(/R\$|%/g, "").trim() || "";

  const parsedVal = parseBrazilNumber(rawVal);
  const parsedPerc = parseBrazilNumber(rawPerc);

  const active = document.activeElement?.id;

  let entradaVal = 0;
  let entradaPerc = 0;

  if (active === "parcela_valor_0" && rawVal !== "") {
    entradaVal = parsedVal;
    entradaPerc = total ? (entradaVal / total * 100) : 0;
  } else if (active === "parcela_percentual_0" && rawPerc !== "") {
    entradaPerc = parsedPerc;
    entradaVal = (entradaPerc / 100) * total;
  } else {
    if (rawVal !== "") {
      entradaVal = parsedVal;
      entradaPerc = total ? (entradaVal / total * 100) : 0;
    } else if (rawPerc !== "") {
      entradaPerc = parsedPerc;
      entradaVal = (entradaPerc / 100) * total;
    }
  }

  if (entradaVal > total) { entradaVal = total; entradaPerc = 100; }
  if (entradaPerc > 100) entradaPerc = 100;

  let restante = Math.max(0, total - entradaVal);
  const valorParcela = qtdParcelas ? (restante / qtdParcelas) : 0;

  let vplTotal = 0;

  rows.forEach(div => {
    const rid = String(div.dataset.row);
    const isEntrada = rid === "0";

    const valEl = document.getElementById(`parcela_valor_${rid}`);
    const percEl = document.getElementById(`parcela_percentual_${rid}`);
    const diasEl = document.getElementById(`parcela_dias1_${rid}`);
    const restanteEl = document.getElementById(`parcela_restante_${rid}`);
    const perdaEl = document.getElementById(`parcela_perda_${rid}`);
    const vplEl = document.getElementById(`parcela_vpl_${rid}`);
    const jurosEl = document.getElementById(`parcela_juros_${rid}`);

    if (isEntrada) {
      if (document.activeElement?.id !== `parcela_valor_0`) {
        valEl.value = entradaVal ? fmtMoney(entradaVal) : "";
      }
      if (document.activeElement?.id !== `parcela_percentual_0`) {
        percEl.value = entradaPerc ? fmtPercent(entradaPerc) : "";
      }

      restante = Math.max(0, total - entradaVal);
      restanteEl.value = restante ? fmtMoney(restante) : "";

      const dias = parseInt(diasEl?.value) || 0;
      diasEl.value = String(dias);

      const perda = Math.pow(1 + jurosTaxa, (dias/30)) - 1;
      perdaEl.value = perda ? fmtPercent(perda*100) : "";

      const vpl = entradaVal - (entradaVal * perda);
      vplEl.value = vpl ? fmtMoney(vpl) : "";
      jurosEl.value = (entradaVal && vpl) ? fmtMoney(entradaVal - vpl) : "";

      if (vpl) vplTotal += vpl;
    } else {
      const v = valorParcela;
      valEl.value = v ? fmtMoney(v) : "";

      const perc = total ? (v / total * 100) : 0;
      percEl.value = perc ? fmtPercent(perc) : "";

      const dias = parseInt(diasEl?.value) || (30 * Number(rid));
      diasEl.value = String(dias);

      restante = Math.max(0, restante - v);
      restanteEl.value = restante ? fmtMoney(restante) : "";

      const perda = Math.pow(1 + jurosTaxa, (dias/30)) - 1;
      perdaEl.value = perda ? fmtPercent(perda*100) : "";

      const vpl = v - (v * perda);
      vplEl.value = vpl ? fmtMoney(vpl) : "";
      jurosEl.value = (v && vpl) ? fmtMoney(v - vpl) : "";

      if (vpl) vplTotal += vpl;
    }
  });

  const jurosTotal = total - vplTotal;
  const totalJurosEl = document.getElementById("parcelas_juros_total");
  if (totalJurosEl) totalJurosEl.value = jurosTotal ? fmtMoney(jurosTotal) : "";
}
