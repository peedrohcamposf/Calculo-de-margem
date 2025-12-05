(function () {

    const EMPRESA_FILIAIS = (window.EMPRESA_FILIAIS || {});

    const empresaSelect = document.getElementById("empresa");
    const filialSelect = document.getElementById("filial");
    const submitBtn = document.getElementById("btn-submit");

    function preencherFiliais() {
        if (!empresaSelect || !filialSelect) return;

        const empresa = empresaSelect.value;
        const filiais = EMPRESA_FILIAIS[empresa] || [];
        const filialAtual = filialSelect.value;

        filialSelect.innerHTML = "";

        filiais.forEach(function (nome) {
            const opt = document.createElement("option");
            opt.value = nome;
            opt.textContent = nome;
            filialSelect.appendChild(opt);
        });

        if (filialAtual && filiais.includes(filialAtual)) {
            filialSelect.value = filialAtual;
        }
    }

    function atualizarTemaEmpresa() {
        if (!empresaSelect || !submitBtn) return;

        const isBrasifAgro = empresaSelect.value === "brasifagro";

        if (isBrasifAgro) {
            submitBtn.classList.remove("btn-primary");
            submitBtn.classList.add("btn-danger");
        } else {
            submitBtn.classList.add("btn-primary");
            submitBtn.classList.remove("btn-danger");
        }
    }

    if (empresaSelect && filialSelect) {
        empresaSelect.addEventListener("change", function () {
            preencherFiliais();
            atualizarTemaEmpresa();
        });

        // Estado inicial
        if (empresaSelect.value) {
            preencherFiliais();
        }
        atualizarTemaEmpresa();
    }
})();

(function () {
    const MAX_LINHAS_OPCIONAIS = 100;
    const tbody = document.getElementById("opcionais-rows");
    const btnAdd = document.getElementById("btn-add-opcional");

    if (!tbody || !btnAdd) {
        return;
    }

    function contarLinhas() {
        return tbody.querySelectorAll("tr.opcional-row").length;
    }

    function atualizarEstadoBotao() {
        btnAdd.disabled = contarLinhas() >= MAX_LINHAS_OPCIONAIS;
    }

    function criarLinhaVazia() {
        const tr = document.createElement("tr");
        tr.className = "opcional-row";
        tr.innerHTML = `
            <td>
                <input type="text"
                       name="opcional_nome"
                       class="form-control form-control-sm"
                       maxlength="150"
                       placeholder="Ex.: AGREGA KIT INVERSÃO">
            </td>
            <td>
                <div class="input-group input-group-sm">
                    <input type="text"
                           name="opcional_horas"
                           class="form-control text-end"
                           placeholder="0,00">
                    <span class="input-group-text">h</span>
                </div>
            </td>
            <td class="text-center">
                <button type="button"
                        class="btn btn-outline-danger btn-sm"
                        onclick="removerOpcionalRow(this)"
                        title="Remover linha">
                    &times;
                </button>
            </td>
        `;
        return tr;
    }

    btnAdd.addEventListener("click", function () {
        if (contarLinhas() >= MAX_LINHAS_OPCIONAIS) {
            return;
        }
        tbody.appendChild(criarLinhaVazia());
        atualizarEstadoBotao();
    });

    window.removerOpcionalRow = function (btn) {
        const tr = btn.closest("tr.opcional-row");
        if (!tr) {
            return;
        }
        tbody.removeChild(tr);
        atualizarEstadoBotao();
    };

    atualizarEstadoBotao();
})();
