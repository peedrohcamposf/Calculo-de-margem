import { parseBrazilNumber } from "../utils/numbers.js";
import { parcelas, setParcelas } from "../core/state.js";
import { attachFormatting } from "../core/formatting.js";
import { computeAll } from "./calc.js";

// ======================================================
//   FUNÇÃO: GERAR APENAS PARCELAS NORMAIS
// ======================================================
export function gerarParcelasNormais(qtd) {
  const arr = [];

  for (let i = 1; i <= qtd; i++) {
    arr.push({
      row: i,
      parcelaNum: i,
      dias1: 30 * i,         // agora EDITÁVEL
      valorParcela: 0,
      percentual: 0,
      dias2: 0,
      jurosPercent: 0,
      vpl: 0,
      juros: 0
    });
  }

  setParcelas(arr);
  renderParcelas();
  attachFormatting();
  computeAll();
}


// ======================================================
//   FUNÇÃO: GERAR LINHA "ENTRADA" + PARCELAMENTO
// ======================================================
export function gerarEntradaMaisParcelas(qtdParcelas) {
  const arr = [];

  // 🟦 Entrada
  arr.push({
    row: 0,
    parcelaNum: "ENTRADA",
    dias1: 0,            // EDITÁVEL
    valorParcela: 0,
    percentual: 0,
    dias2: 0,
    jurosPercent: 0,
    vpl: 0,
    juros: 0
  });

  // 🟦 Parcelas normais
  for (let i = 1; i <= qtdParcelas; i++) {
    arr.push({
      row: i,
      parcelaNum: i,
      dias1: 30 * i,
      valorParcela: 0,
      percentual: 0,
      dias2: 0,
      jurosPercent: 0,
      vpl: 0,
      juros: 0
    });
  }

  setParcelas(arr);
  renderParcelas();
  attachFormatting();
  computeAll();
}


// ======================================================
//   FUNÇÃO: LIMPAR TODAS AS PARCELAS
// ======================================================
export function limparParcelas() {
  setParcelas([]);
  const list = document.getElementById("parcelasList");
  if (list) list.innerHTML = "";
}


// ======================================================
//   FUNÇÃO: ADICIONAR PARCELA "À VISTA"
// ======================================================
export function adicionarParcelaAvista() {
  const p = {
    row: 1,
    parcelaNum: "À vista",
    dias1: 0,
    valorParcela: 0,
    percentual: 100,
    dias2: 0,
    jurosPercent: 0,
    vpl: 0,
    juros: 0
  };

  setParcelas([p]);
  renderParcelas();
  attachFormatting();
  computeAll();
}


// ======================================================
//   FUNÇÃO: RENDERIZAR PARCELAS NO DOM
// ======================================================
export function renderParcelas() {
  const list = document.getElementById("parcelasList");
  if (!list) return;
  list.innerHTML = "";

  parcelas.forEach(p => {
    const el = document.createElement("div");
    el.className = "cheader";

    el.innerHTML = `
      <div class="row g-2 align-items-center">

        <!-- Nº da parcela -->
        <div class="col-header">
        <div class="field-label">${p.row === 0? "Entrada": `${p.parcelaNum}º Parcela`}
        </div>

        </div>

        <!-- Dias (AGORA EDITÁVEL) -->
        <div class="col-header">
          <input id="parcela_dias1_${p.row}" class="form-control numeric" value="${p.dias1}">
        </div>

        <!-- Valor -->
        <div class="col-header">
          <input id="parcela_valor_${p.row}" class="form-control numeric" value="${p.valorParcela}">
        </div>

        <!-- Percentual -->
        <div class="col-header">
          <input id="parcela_percentual_${p.row}" class="form-control numeric" value="${p.percentual}">
        </div>

        <!-- Dias extra -->
        <div class="col-header">
          <input id="parcela_dias2_${p.row}" class="form-control numeric" value="${p.dias2}">
        </div>

        <!-- Juros % -->
        <div class="col-header">
          <input id="parcela_jurosPercent_${p.row}" class="form-control numeric" value="${p.jurosPercent}">
        </div>

        <!-- VPL -->
        <div class="col-header">
          <input id="parcela_vpl_${p.row}" class="form-control" readonly value="${p.vpl}">
        </div>

        <!-- Juros -->
        <div class="col-header">
          <input id="parcela_juros_${p.row}" class="form-control" readonly value="${p.juros}">
        </div>
      </div>
    `;

    list.appendChild(el);
  });
}
