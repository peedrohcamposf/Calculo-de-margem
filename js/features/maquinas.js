// Calculo_de_margem/js/features/maquinas.js
import { parseBrazilNumber, formatBrazilNumber, safeDiv } from "../utils/numbers.js";
import { maquinas, setMaquinas } from "../core/state.js";
import { attachFormatting } from "../core/formatting.js";
import { computeAll } from "./calc.js";

// IMPORT CORRETO da função de autocomplete (está no seu ZIP em /data/)
import { attachAutocompleteToRow } from "../../data/autocompleteMaquinas.js";

// Sincroniza o estado global a partir do DOM (leitura das linhas)
export function syncMaquinasFromDOM() {
  const rows = Array.from(document.querySelectorAll(".maquina-row"));
  const newArr = [];

  rows.forEach((rowEl, idx) => {
    const marca   = rowEl.querySelector(".inpMarca")?.value || "";
    const tipo    = rowEl.querySelector(".inpTipo")?.value || "";
    const modelo  = rowEl.querySelector(".inpModelo")?.value || "";
    const codigo  = rowEl.querySelector(".inpCodigo")?.value || "";
    const valorV  = rowEl.querySelector('[data-field="Q"]')?.value || "";
    const quant   = rowEl.querySelector('[data-field="N"]')?.value || "";
    const agrega  = rowEl.querySelector('[data-field="O"]')?.value || "";
    const valorC  = rowEl.querySelector(".inpValorCompra")?.value || "";

    newArr.push({
      id: rowEl.dataset.uid || null,
      row: idx + 1,
      maquinaNum: idx + 1,

      // campos usados no restante do projeto
      I: marca,    // Marca
      T: tipo,     // Tipo
      L: modelo,   // Modelo
      C: codigo,   // Código
      Q: valorV,   // Valor de venda (cada)
      N: quant,    // Quantidade
      O: agrega,   // Agrega/Desagrega

      valorCompra: valorC
    });
  });

  setMaquinas(newArr);
}

// Adiciona uma máquina vazia ao estado e renderiza
export function addMaquinaEmpty() {
  syncMaquinasFromDOM();
  const nextIndex = maquinas.length + 1;

  maquinas.push({
    id: null,
    row: nextIndex,
    maquinaNum: nextIndex,
    I: "",
    T: "",
    L: "",
    C: "",
    Q: "",
    N: "",
    O: ""
  });

  renderMaquinas();
  attachFormatting();
  computeAll();

  // foca no input Marca da nova linha
  setTimeout(() => {
    const el = document.querySelector(`.maquina-row:last-child .inpMarca`);
    if (el) el.focus();
  }, 50);
}

// Renderiza todas as linhas a partir do estado `maquinas`
export function renderMaquinas() {
  const list = document.getElementById("maquinasList");
  if (!list) return;
  list.innerHTML = "";

  if (maquinas.length === 0) return;

  maquinas.forEach((m, index) => {
    const rowIndex = index + 1;

    const el = document.createElement("div");
    el.className = "cheader d-flex align-items-center text-center maquina-row";
    el.dataset.index = rowIndex;
    if (m.id) el.dataset.uid = m.id;

    el.innerHTML = `
      <div class="row g-2 align-items-center">

        <div class="col-header">
          <input class="form-control inpMarca" value="${m.I || ""}" />
        </div>

        <div class="col-header">
          <input class="form-control inpTipo" value="${m.T || ""}" />
        </div>

        <div class="col-header">
          <input class="form-control inpModelo" value="${m.L || ""}" data-field="L" />
        </div>

        <div class="col-header">
          <input class="form-control inpCodigo" value="${m.C || ""}" />
        </div>

        <div class="col-header">
          <input class="form-control" data-field="Q" value="${m.Q || ""}" />
        </div>

        <div class="col-header">
          <input class="form-control" data-field="N" value="${m.N || ""}" />
        </div>

        <div class="col-header">
          <input class="form-control" data-field="O" value="${m.O || ""}" />
        </div>

        <div class="col-header">
          <input class="form-control inpValorCompra" readonly value="${m.valorCompra || ""}" />
        </div>

        <div class="col-auto">
          <button class="btn btn-danger btn-sm btnRemoveMaquina">Remover</button>
        </div>

      </div>
    `;

    // adiciona a linha ao DOM
    list.appendChild(el);

    // --------------------------
    // Anexa autocomplete (AGORA IMPORTADO CORRETAMENTE)
    // --------------------------
    try {
      attachAutocompleteToRow(el);
    } catch (err) {
      // Logar o erro para diagnóstico — não deixar quebrar toda a inicialização
      console.error("Erro ao anexar autocomplete na linha:", err);
    }

    // Botão remover
    el.querySelector(".btnRemoveMaquina").addEventListener("click", () => {
      syncMaquinasFromDOM();
      maquinas.splice(index, 1);

      maquinas.forEach((item, idx) => {
        item.row = idx + 1;
        item.maquinaNum = idx + 1;
      });

      renderMaquinas();
      attachFormatting();
      computeAll();
    });
  });
}
