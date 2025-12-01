// js/features/maquinas.js
import { parseBrazilNumber, formatBrazilNumber } from "../utils/numbers.js";
import { maquinas, setMaquinas } from "../core/state.js";
import { attachFormatting } from "../core/formatting.js";
import { computeAll } from "./calc.js";
import { attachAutocompleteToRow } from "../../data/autocompleteMaquinas.js";

/**
 * Correção:
 * - syncMaquinasFromDOM agora LÊ o valor de compra da célula (.inpValorCompra)
 *   e o salva no estado (como string numérica sem formatação) exatamente
 *   como os outros campos. Assim ao adicionar nova linha o valor de compra
 *   existente NÃO some mais.
 *
 * - renderMaquinas mostra o valorCompra formatado (R$) a partir do estado,
 *   e armazena o raw no atributo data-raw para leitura futura.
 *
 * - escapeHtml para segurança ao injetar valores.
 */

/* Sincroniza estado a partir do DOM (agora inclui valorCompra) */
export function syncMaquinasFromDOM() {
  const rows = Array.from(document.querySelectorAll(".maquina-row"));
  const newArr = [];

  rows.forEach((rowEl, idx) => {
    const marca  = rowEl.querySelector(".inpMarca")?.value || "";
    const tipo   = rowEl.querySelector(".inpTipo")?.value || "";
    const modelo = rowEl.querySelector(".inpModelo")?.value || "";
    const codigo = rowEl.querySelector(".inpCodigo")?.value || "";

    const valorVendaEl = rowEl.querySelector('[data-field="Q"]');
    const quantEl      = rowEl.querySelector('[data-field="N"]');
    const agregaEl     = rowEl.querySelector('[data-field="O"]');

    const valorVenda = valorVendaEl?.value || "";
    const quant      = quantEl?.value || "";
    const agrega     = agregaEl?.value || "";

    // Lê valorCompra preferindo o atributo data-raw (que renderMaquinas define),
    // caso não exista tenta ler o value e dessufixar "R$".
    let valorCompraRaw = rowEl.querySelector(".inpValorCompra")?.dataset.raw ?? "";

    if (!valorCompraRaw) {
      // fallback para value exibido (formatado) -> remover R$ e pontos/virgula
      const displayed = rowEl.querySelector(".inpValorCompra")?.value || "";
      valorCompraRaw = String(displayed).replace(/\s?R\$\s?/g, "").trim();
    }

    // Normaliza para um número "cru" (usar parseBrazilNumber para aceitar "1.234,56")
    const valorCompraNum = parseBrazilNumber(valorCompraRaw);
    const valorCompraStored = (String(valorCompraRaw).trim() === "") ? "" : String(valorCompraNum);

    newArr.push({
      id: rowEl.dataset.uid || null,
      row: idx + 1,
      maquinaNum: idx + 1,
      I: marca,
      T: tipo,
      L: modelo,
      C: codigo,
      Q: valorVenda,
      N: quant,
      O: agrega,
      // salvo como string numérica (ex: "500000") ou "" se vazio
      valorCompra: valorCompraStored
    });
  });

  setMaquinas(newArr);
}

/* Adiciona máquina vazia */
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
    O: "",
    valorCompra: "" // sem valor por padrão
  });

  renderMaquinas();
  attachFormatting();
  computeAll();

  setTimeout(() => {
    const el = document.querySelector(`.maquina-row:last-child .inpMarca`);
    if (el) el.focus();
  }, 60);
}

/* Renderiza máquinas a partir do estado (valorCompra vem do state e é formatado) */
export function renderMaquinas() {
  const list = document.getElementById("maquinasList");
  if (!list) return;
  list.innerHTML = "";

  if (!maquinas || maquinas.length === 0) return;

  maquinas.forEach((m, index) => {
    const rawValorCompra = (m.valorCompra && String(m.valorCompra).trim() !== "") ? m.valorCompra : "";
    const valorCompraFmt = rawValorCompra ? formatBrazilNumber(parseBrazilNumber(String(rawValorCompra))) + " R$" : "";

    const el = document.createElement("div");
    el.className = "cheader d-flex align-items-center text-center maquina-row";
    el.dataset.index = index + 1;
    if (m.id) el.dataset.uid = m.id;

    el.innerHTML = `
      <div class="row g-2 align-items-center">
        <div class="col-header"><input class="form-control inpMarca" value="${escapeHtml(m.I || "")}"></div>
        <div class="col-header"><input class="form-control inpTipo" value="${escapeHtml(m.T || "")}"></div>
        <div class="col-header"><input class="form-control inpModelo" data-field="L" value="${escapeHtml(m.L || "")}"></div>
        <div class="col-header"><input class="form-control inpCodigo" value="${escapeHtml(m.C || "")}"></div>
        <div class="col-header"><input class="form-control numeric" data-field="Q" data-type="money" value="${escapeHtml(m.Q || "")}"></div>
        <div class="col-header"><input class="form-control numeric" data-field="N" data-type="int" value="${escapeHtml(m.N || "")}"></div>
        <div class="col-header"><input class="form-control numeric" data-field="O" data-type="money" value="${escapeHtml(m.O || "")}"></div>
        <div class="col-header">
          <input class="form-control inpValorCompra" readonly
                 data-raw="${escapeHtml(rawValorCompra)}"
                 value="${escapeHtml(valorCompraFmt)}">
        </div>
        <div class="col-auto"><button class="btn btn-danger btn-sm btnRemoveMaquina">Remover</button></div>
      </div>
    `;

    list.appendChild(el);

    // Anexa autocomplete (se disponível) — não deve quebrar a página se falhar
    try { attachAutocompleteToRow(el); } catch (err) { console.debug("autocomplete attach error", err); }

    // Remover
    el.querySelector(".btnRemoveMaquina").addEventListener("click", () => {
      syncMaquinasFromDOM();
      maquinas.splice(index, 1);
      maquinas.forEach((item, idx) => { item.row = idx + 1; item.maquinaNum = idx + 1; });
      renderMaquinas();
      attachFormatting();
      computeAll();
    });
  });

  // reaplica formatação e recalc
  attachFormatting();
  document.dispatchEvent(new Event("recompute"));
}

function escapeHtml(s) {
  return String(s || "").replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;");
}
