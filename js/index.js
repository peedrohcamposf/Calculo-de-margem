import { 
    limparParcelas, 
    gerarParcelasNormais, 
    adicionarParcelaAvista,
    gerarEntradaMaisParcelas 
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

  // =============================
  //     SWITCH TIPO DE VENDA
  // =============================
  const tipoVendaSelect = document.getElementById("TipoVenda");
  const qtdParcelasInput = document.getElementById("qtdParcelas");

  function handleVendaFinanciada() {
    qtdParcelasInput.disabled = false;
    qtdParcelasInput.value = "";

    limparParcelas();

    // quando o usuário digitar quantidade → gerar entrada + parcelas
    qtdParcelasInput.oninput = () => {
      limparParcelas();

      const qtd = parseInt(qtdParcelasInput.value);
      if (!isNaN(qtd) && qtd > 0) {
        gerarEntradaMaisParcelas(qtd);
      }
    };
  }

  function handleVendaAvista() {
    qtdParcelasInput.disabled = true;
    qtdParcelasInput.value = 1;

    limparParcelas();
    adicionarParcelaAvista();
  }

  if (tipoVendaSelect) {
    tipoVendaSelect.addEventListener("change", () => {
      const tipo = tipoVendaSelect.value;

      switch (tipo) {
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

    // executa comportamento inicial
    tipoVendaSelect.dispatchEvent(new Event("change"));
  }

  inicializarHeaderCorporativo();
  padronizarDropdowns();
  initThemeSwitcher();
  initFilialDropdown();

  document.addEventListener("recompute", computeAll);
});
