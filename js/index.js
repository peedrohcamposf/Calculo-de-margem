import { updateParcelas } from "./features/parcelas.js";
import { renderMaquinas, addMaquinaEmpty } from "./features/maquinas.js";
import { attachFormatting } from "./core/formatting.js";
import { computeAll } from "./features/calc.js";
import { inicializarHeaderCorporativo } from "./features/header.js";
import { initThemeSwitcher } from "./features/theme.js";
import { padronizarDropdowns, initFilialDropdown } from "./features/dropdowns.js";
import { setMaquinas, setParcelas } from "./core/state.js";

document.addEventListener("DOMContentLoaded", () => {

  // inicia parcelas
  updateParcelas();

  // inicia máquinas
  setMaquinas([]);
  renderMaquinas();
  attachFormatting();
  computeAll();

  // evento global de recálculo
  document.addEventListener("recompute", computeAll);

  // botão adicionar máquina
  const btnAddMaquina = document.getElementById("btnAddMaquina");
  if (btnAddMaquina) btnAddMaquina.addEventListener("click", addMaquinaEmpty);

  // reset geral
  const resetBtn = document.getElementById("resetBtn");
  if (resetBtn) resetBtn.addEventListener("click", () => {
    setParcelas([]);
    setMaquinas([]);
    document.getElementById("parcelasList").innerHTML = "";
    document.getElementById("maquinasList").innerHTML = "";
    updateParcelas();
    computeAll();
  });

  inicializarHeaderCorporativo();
  padronizarDropdowns();
  initThemeSwitcher();
  initFilialDropdown();
});
