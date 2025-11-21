// parcelas.js
import { parseBrazilNumber } from "../utils/numbers.js";
import { parcelas, setParcelas } from "../core/state.js";
import { attachFormatting } from "../core/formatting.js";
import { computeAll } from "./calc.js";

/**
 * Gera o array de parcelas a partir do input #qtdParcelas (ou variantes de id)
 * Retorna um array com objetos representando cada parcela.
 */
export function gerarParcelas() {
  const el = document.getElementById("qtdParcelas")
          || document.getElementById("QtdParcelas")
          || document.querySelector("[name='qtdParcelas']");

  const raw = el?.value ?? "";
  const parsed = parseInt(String(raw).trim(), 10);
  const qtd = Number.isNaN(parsed) ? 0 : Math.max(0, parsed);

  const arr = [];
  for (let i = 0; i < qtd; i++) {
    arr.push({
      row: i + 1,
      parcelaNum: i + 1,
      // valores padrão — podem ser atualizados via inputs gerados
      dias1: 30 * (i + 1),    // coluna 2 (ex.: prazo)
      valorParcela: 0,        // coluna 3 (input)
      percentual: 0,          // coluna 4 (input)
      dias2: 0,               // coluna 5 (input)
      jurosPercent: 0,        // coluna 6 (input)
      vpl: 0,                 // coluna 7 (calculo)
      juros: 0                // coluna 8 (calculo)
    });
  }

  return arr;
}

/**
 * Atualiza o estado global de parcelas e re-renderiza
 */
export function updateParcelas() {
  setParcelas(gerarParcelas());
  renderParcelas();
  attachFormatting();
  computeAll();
}

/**
 * Renderiza as parcelas no container #parcelasList
 * Gera 8 colunas, alinhadas com seu header.
 */
export function renderParcelas() {
  const list = document.getElementById("parcelasList");
  if (!list) return;
  list.innerHTML = "";

  if (!parcelas || parcelas.length === 0) return;

  parcelas.forEach(p => {
    const el = document.createElement("div");
    el.className = "cheader";
    el.dataset.row = p.row;

    el.innerHTML = `
      <div class="row g-2 align-items-center">
        <!-- 1: Parcela (nº) -->
        <div class="col-header">
          <div class="field-label">${p.parcelaNum}ª</div>
        </div>

        <!-- 2: Dias (fixo/auto) -->
        <div class="col-header">
          <input id="parcela_dias1_${p.row}" class="form-control" readonly value="${p.dias1}">
        </div>

        <!-- 3: Valor da Parcela (input) -->
        <div class="col-header">
          <input id="parcela_valor_${p.row}" class="form-control numeric" value="${p.valorParcela}">
        </div>

        <!-- 4: % da Parcela (input) -->
        <div class="col-header">
          <input id="parcela_percentual_${p.row}" class="form-control numeric" value="${p.percentual}">
        </div>

        <!-- 5: Dias (extra/input) -->
        <div class="col-header">
          <input id="parcela_dias2_${p.row}" class="form-control numeric" value="${p.dias2}">
        </div>

        <!-- 6: Juros % (input) -->
        <div class="col-header">
          <input id="parcela_jurosPercent_${p.row}" class="form-control numeric" value="${p.jurosPercent}">
        </div>

        <!-- 7: VPL (resultado/calculado) -->
        <div class="col-header">
          <input id="parcela_vpl_${p.row}" class="form-control" readonly value="${p.vpl}">
        </div>

        <!-- 8: Juros (resultado/calculado) -->
        <div class="col-header">
          <input id="parcela_juros_${p.row}" class="form-control" readonly value="${p.juros}">
        </div>
      </div>
    `;

    list.appendChild(el);
  });
}

/**
 * Auto-inicialização: liga listener ao input #qtdParcelas e renderiza ao carregar.
 * - Se sua aplicação já chama updateParcelas() em outro lugar, isso não atrapalha.
 * - Mantém-se defensivo para ids variantes.
 */
function initParcelasAuto() {
  function tryAttach() {
    const el = document.getElementById("qtdParcelas")
            || document.getElementById("QtdParcelas")
            || document.querySelector("[name='qtdParcelas']");

    if (el) {
      // liga ao evento input (digitar/alterar)
      el.addEventListener("input", () => {
        updateParcelas();
      });

      // renderiza uma vez para o estado inicial
      updateParcelas();
    } else {
      // se não achou ainda, tenta novamente em 200ms (caso DOM carregue mais tarde)
      setTimeout(tryAttach, 200);
    }
  }

  // aguarda DOM ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", tryAttach);
  } else {
    tryAttach();
  }
}

// inicia automaticamente
initParcelasAuto();

// export padrão (opcional)
export default {
  gerarParcelas,
  updateParcelas,
  renderParcelas
};
