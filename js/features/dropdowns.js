export const filiaisPorEmpresa = {
  Brasif: [
    "Belo Horizonte", "Brasilia", "Cuiabá", "Curitiba",
    "Goiânia", "Jundiaí", "Palmas", "Ribeirão Preto",
    "Rio de Janeiro", "Serra"
  ],
  Maxum: [
    "Luís Eduardo Magalhães", "Roda Velha",
    "Correntina", "Formosa do Rio Preto", "Bom Jesus"
  ]
};

export function padronizarDropdowns() {
  document.querySelectorAll("select").forEach(sel => sel.classList.add("form-select"));
}

export function atualizarFiliais(selectEmpresa, selectFilial) {
  const empresaSelecionada = selectEmpresa?.value;
  selectFilial.innerHTML = "";

  if (empresaSelecionada && filiaisPorEmpresa[empresaSelecionada]) {
    const placeholder = document.createElement("option");
    placeholder.value = "";
    placeholder.disabled = true;
    placeholder.selected = true;
    placeholder.textContent = "Selecione a Filial";
    selectFilial.appendChild(placeholder);

    filiaisPorEmpresa[empresaSelecionada].forEach(f => {
      const opt = document.createElement("option");
      opt.value = f;
      opt.textContent = f;
      selectFilial.appendChild(opt);
    });
  } else {
    const opt = document.createElement("option");
    opt.value = "";
    opt.disabled = true;
    opt.selected = true;
    opt.textContent = "Selecione uma empresa primeiro";
    selectFilial.appendChild(opt);
  }
}

export function initFilialDropdown() {
  const selectEmpresa = document.getElementById("empresa");
  const selectFilial = document.getElementById("filial");

  if (!selectEmpresa || !selectFilial) return;

  if (!selectEmpresa.querySelector('option[value=""]')) {
    const placeholderOpt = document.createElement("option");
    placeholderOpt.value = "";
    placeholderOpt.textContent = "Selecione uma empresa";
    placeholderOpt.selected = true;
    placeholderOpt.disabled = true;
    selectEmpresa.insertBefore(placeholderOpt, selectEmpresa.firstChild);
  }

  selectEmpresa.addEventListener("change", () =>
    atualizarFiliais(selectEmpresa, selectFilial)
  );

  atualizarFiliais(selectEmpresa, selectFilial);
}
