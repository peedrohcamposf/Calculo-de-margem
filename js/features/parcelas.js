// js/features/parcelas.js
import { parcelas, setParcelas } from "../core/state.js";
import { attachFormatting } from "../core/formatting.js";

/* Helper to show raw values (computeAll will format) */
function safeFormat(n) {
  if (n === null || n === undefined || n === "") return "";
  return String(n);
}

export function gerarEntradaMaisParcelas(qtdParcelas) {
  const arr = [];
  arr.push({ row: 0, parcelaNum: "Entrada", dias1: 0, valorParcela: 0, percentual: 0, restante: 0, perdaPercent: 0, vpl: 0, juros: 0 });
  for (let i=1;i<=qtdParcelas;i++) {
    arr.push({ row: i, parcelaNum: i, dias1: 30*i, valorParcela: 0, percentual: 0, restante: 0, perdaPercent: 0, vpl: 0, juros: 0 });
  }
  setParcelas(arr);
  renderParcelas();
  attachFormatting();
  attachListenersToParcelas();
  document.dispatchEvent(new Event("recompute"));
}

export function gerarParcelasNormais(qtd) { gerarEntradaMaisParcelas(qtd); }

export function limparParcelas() {
  setParcelas([]);
  const list = document.getElementById("parcelasList");
  if (list) list.innerHTML = "";
  document.dispatchEvent(new Event("recompute"));
}

export function adicionarParcelaAvista() {
  setParcelas([{ row:1, parcelaNum: "À vista", dias1:0, valorParcela:0, percentual:100, restante:0, perdaPercent:0, vpl:0, juros:0 }]);
  renderParcelas();
  attachFormatting();
  attachListenersToParcelas();
  document.dispatchEvent(new Event("recompute"));
}

export function renderParcelas() {
  const list = document.getElementById("parcelasList");
  if (!list) return;
  list.innerHTML = "";

  parcelas.forEach(p => {
    const id = p.row;
    const isEntrada = id === 0;
    const wrapper = document.createElement("div");
    wrapper.className = "cheader";
    wrapper.dataset.row = id;

    wrapper.innerHTML = `
      <div class="row g-2 align-items-center">
        <div class="col-header"><div class="field-label">${isEntrada ? "Entrada" : `${p.parcelaNum}º Parcela`}</div></div>
        <div class="col-header"><input id="parcela_valor_${id}" class="form-control numeric" data-type="money" value="${safeFormat(p.valorParcela)}" ${isEntrada ? "" : "readonly"}></div>
        <div class="col-header"><input id="parcela_percentual_${id}" class="form-control numeric" data-type="percent" value="${safeFormat(p.percentual)}" ${isEntrada ? "" : "readonly"}></div>
        <div class="col-header"><input id="parcela_dias1_${id}" class="form-control numeric" data-type="int" value="${safeFormat(p.dias1)}" ${isEntrada ? "" : "readonly"}></div>
        <div class="col-header"><input id="parcela_restante_${id}" class="form-control" readonly data-type="money" value="${safeFormat(p.restante)}"></div>
        <div class="col-header"><input id="parcela_perda_${id}" class="form-control" readonly data-type="percent" value="${safeFormat(p.perdaPercent)}"></div>
        <div class="col-header"><input id="parcela_vpl_${id}" class="form-control" readonly data-type="money" value="${safeFormat(p.vpl)}"></div>
        <div class="col-header"><input id="parcela_juros_${id}" class="form-control" readonly data-type="money" value="${safeFormat(p.juros)}"></div>
      </div>
    `;
    list.appendChild(wrapper);
  });
}

function attachListenersToParcelas() {
  ["parcela_valor_0","parcela_percentual_0","parcela_dias1_0","Juros_taxa"].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener("input", () => document.dispatchEvent(new Event("recompute")));
  });
}
