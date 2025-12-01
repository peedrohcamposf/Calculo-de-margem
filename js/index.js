import { 
  limparParcelas, 
  gerarEntradaMaisParcelas, 
  adicionarParcelaAvista
} from "./features/parcelas.js";

import { renderMaquinas, addMaquinaEmpty } from "./features/maquinas.js";
import { attachFormatting } from "./core/formatting.js";
import { computeAll } from "./features/calc.js";
import { inicializarHeaderCorporativo } from "./features/header.js";
import { initThemeSwitcher } from "./features/theme.js";
import { padronizarDropdowns, initFilialDropdown } from "./features/dropdowns.js";
import { setMaquinas } from "./core/state.js";

document.addEventListener("DOMContentLoaded", () => {

  // inicia máquinas
  setMaquinas([]);
  renderMaquinas();
  attachFormatting();
  computeAll();

  // botão adicionar máquina
  document.getElementById("btnAddMaquina")?.addEventListener("click", addMaquinaEmpty);

  // ============================================
  //     SWITCH TIPO DE VENDA + PARCELAS
  // ============================================
  const tipoVendaSelect = document.getElementById("TipoVenda");
  let qtdParcelasInput = document.getElementById("qtdParcelas");

  // 🔄 Recria o input e sempre recoloca listener
  function resetQtdParcelasInput() {
    const novo = qtdParcelasInput.cloneNode(true);
    qtdParcelasInput.parentNode.replaceChild(novo, qtdParcelasInput);
    qtdParcelasInput = novo;

    // SEMPRE reanexa listener aqui
    qtdParcelasInput.addEventListener("input", atualizarParcelas);
  }

  // 🔥 Atualiza parcelas conforme digitado
  function atualizarParcelas() {
    const valor = qtdParcelasInput.value.trim();

    if (valor === "") {
      limparParcelas();
      return;
    }

    const numero = parseInt(valor);

    if (isNaN(numero) || numero <= 0) {
      limparParcelas();
      return;
    }

    if (tipoVendaSelect.value === "VendaFinanciada") {
      gerarEntradaMaisParcelas(numero);
    } else {
      adicionarParcelaAvista();
    }
  }

  // 🔵 Venda financiada
  function handleVendaFinanciada() {
    resetQtdParcelasInput();
    qtdParcelasInput.disabled = false;
    qtdParcelasInput.value = "";
    limparParcelas();
  }

  // 🟢 Venda à vista e demais tipos
  function handleVendaAvista() {
    resetQtdParcelasInput();
    qtdParcelasInput.disabled = true;
    qtdParcelasInput.value = 1;
    limparParcelas();
    adicionarParcelaAvista();
  }

  // Listener principal de troca de tipo
  if (tipoVendaSelect) {
    tipoVendaSelect.addEventListener("change", () => {
      switch (tipoVendaSelect.value) {
        case "VendaFinanciada":
          handleVendaFinanciada();
          break;

        case "VendaVista":
        case "VendaPublica":
        case "Consorcio":
        case "CartaoBNDES":
        case "Car":
        case "ADefinir":
        default:
          handleVendaAvista();
          break;
      }
    });

    // comportamento inicial
    tipoVendaSelect.dispatchEvent(new Event("change"));
  }

  inicializarHeaderCorporativo();
  padronizarDropdowns();
  initThemeSwitcher();
  initFilialDropdown();

  document.addEventListener("recompute", computeAll);
});
