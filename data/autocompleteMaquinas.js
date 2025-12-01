import { maquinasDB } from "./maquinasDB.js";

/* ======================================================
   LOOKUP MAPS (ALTÍSSIMO DESEMPENHO)
   ====================================================== */
const mapCodigo = new Map();
const mapModelo = new Map();
const mapTipo = new Map();
const mapMarca = new Map();

for (const m of maquinasDB) {
  mapCodigo.set(m.codigo, m);
  mapModelo.set(m.modelo, m);

  if (!mapTipo.has(m.tipo)) mapTipo.set(m.tipo, []);
  mapTipo.get(m.tipo).push(m);

  if (!mapMarca.has(m.marca)) mapMarca.set(m.marca, []);
  mapMarca.get(m.marca).push(m);
}

const uniq = arr => [...new Set(arr)];

function ordenarRelevancia(lista, termo) {
  const t = termo.toLowerCase();

  return lista.sort((a, b) => {
    const al = a.toLowerCase();
    const bl = b.toLowerCase();

    const aStarts = al.startsWith(t);
    const bStarts = bl.startsWith(t);

    if (aStarts && !bStarts) return -1;
    if (!aStarts && bStarts) return 1;

    return al.localeCompare(bl);
  });
}

function filtrarMarcas(txt) {
  const t = txt.toLowerCase();
  return ordenarRelevancia(
    uniq(maquinasDB.filter(m => m.marca.toLowerCase().includes(t)).map(m => m.marca)),
    txt
  );
}

function filtrarTipos(marca, txt) {
  const t = txt.toLowerCase();
  let base = marca ? mapMarca.get(marca) || [] : maquinasDB;

  return ordenarRelevancia(
    uniq(base.filter(m => m.tipo.toLowerCase().includes(t)).map(m => m.tipo)),
    txt
  );
}

function filtrarModelos(marca, tipo, txt) {
  const t = txt.toLowerCase();
  let base = maquinasDB;

  if (marca) base = base.filter(x => x.marca === marca);
  if (tipo) base = base.filter(x => x.tipo === tipo);

  return ordenarRelevancia(
    uniq(base.filter(m => m.modelo.toLowerCase().includes(t)).map(m => m.modelo)),
    txt
  );
}

function filtrarCodigos(marca, tipo, txt) {
  const t = txt.toLowerCase();
  let base = maquinasDB;

  if (marca) base = base.filter(x => x.marca === marca);
  if (tipo) base = base.filter(x => x.tipo === tipo);

  return ordenarRelevancia(
    uniq(base.filter(m => m.codigo.toLowerCase().includes(t)).map(m => m.codigo)),
    txt
  );
}

function debounce(fn, delay = 150) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

/* ======================================================
   FUNÇÕES NOVAS: seleção automática
   ====================================================== */

// tenta identificar se usuário digitou valor exato
function tryAutoSelectExactMatch(input, value, options, row) {
  if (!value) return false;

  const exact = options.find(opt => opt.toLowerCase() === value.toLowerCase());
  if (!exact) return false;

  input.value = exact;

  // ativa preenchimento inteligente
  triggerCascade(input, row);

  return true;
}

function triggerCascade(input, row) {
  const field = input.classList.contains("inpMarca") ? "marca"
            : input.classList.contains("inpTipo") ? "tipo"
            : input.classList.contains("inpModelo") ? "modelo"
            : input.classList.contains("inpCodigo") ? "codigo"
            : null;

  if (!field) return;

  const marca = row.querySelector(".inpMarca");
  const tipo = row.querySelector(".inpTipo");
  const modelo = row.querySelector(".inpModelo");
  const codigo = row.querySelector(".inpCodigo");
  const valor = row.querySelector(".inpValorCompra");

  const txt = input.value;

  if (field === "codigo" && mapCodigo.has(txt)) {
    const m = mapCodigo.get(txt);
    marca.value = m.marca;
    tipo.value = m.tipo;
    modelo.value = m.modelo;
    codigo.value = m.codigo;
    valor.value = m.valorCompra;
  }

  if (field === "modelo" && mapModelo.has(txt)) {
    const m = mapModelo.get(txt);
    marca.value = m.marca;
    tipo.value = m.tipo;
    modelo.value = m.modelo;
    codigo.value = m.codigo;
    valor.value = m.valorCompra;
  }
}

/* ======================================================
   AUTOCOMPLETE PRINCIPAL
   ====================================================== */

export function attachAutocompleteToRow(row) {
  const marca = row.querySelector(".inpMarca");
  const tipo = row.querySelector(".inpTipo");
  const modelo = row.querySelector(".inpModelo");
  const codigo = row.querySelector(".inpCodigo");
  const valor = row.querySelector(".inpValorCompra");

  // Marca
  autocompleteCampo(marca, txt => filtrarMarcas(txt), item => {
    marca.value = item;
    tipo.value = "";
    modelo.value = "";
    codigo.value = "";
    valor.value = "";
  }, row);

  // Tipo
  autocompleteCampo(tipo, txt => filtrarTipos(marca.value, txt), item => {
    tipo.value = item;
    const marcas = uniq(maquinasDB.filter(m => m.tipo === item).map(m => m.marca));
    if (marcas.length === 1) marca.value = marcas[0];
    modelo.value = "";
    codigo.value = "";
    valor.value = "";
  }, row);

  // Modelo
  autocompleteCampo(modelo, txt => filtrarModelos(marca.value, tipo.value, txt), item => {
    const obj = mapModelo.get(item);
    if (obj) {
      marca.value = obj.marca;
      tipo.value = obj.tipo;
      modelo.value = obj.modelo;
      codigo.value = obj.codigo;
      valor.value = obj.valorCompra;
    }
  }, row);

  // Código
  autocompleteCampo(codigo, txt => filtrarCodigos(marca.value, tipo.value, txt), item => {
    const obj = mapCodigo.get(item);
    if (obj) {
      marca.value = obj.marca;
      tipo.value = obj.tipo;
      modelo.value = obj.modelo;
      codigo.value = obj.codigo;
      valor.value = obj.valorCompra;
    }
  }, row);
}

/* ======================================================
   AUTOCOMPLETE VISUAL
   ====================================================== */

function autocompleteCampo(input, fnLista, onSelect, row) {
  let selIndex = -1;

  const handler = debounce(() => {
    if (!input.value.trim()) {
      fecharSugestoes();
      return;
    }

    const lista = fnLista(input.value);

    // 🚀 tentativa automática de match exato ANTES de mostrar dropdown
    if (tryAutoSelectExactMatch(input, input.value.trim(), lista, row)) {
      fecharSugestoes();
      return;
    }

    abrirSugestoes(input, lista, item => {
      onSelect(item);
      fecharSugestoes();
    });

    selIndex = -1;
  });

  input.addEventListener("input", handler);

  input.addEventListener("keydown", e => {
    const box = document.querySelector(".suggestions-box");
    const itens = box ? [...box.querySelectorAll(".suggestion-item")] : [];

    if (e.key === "ArrowDown" && itens.length) {
      e.preventDefault();
      selIndex = (selIndex + 1) % itens.length;
      destacar(itens, selIndex);
      return;
    }

    if (e.key === "ArrowUp" && itens.length) {
      e.preventDefault();
      selIndex = (selIndex - 1 + itens.length) % itens.length;
      destacar(itens, selIndex);
      return;
    }

    if (e.key === "Enter") {
      e.preventDefault();

      // ENTER → seleciona item destacado
      if (selIndex >= 0 && itens[selIndex]) {
        itens[selIndex].click();
        return;
      }

      // ENTER → tenta seleção automática (digitado exato)
      const lista = fnLista(input.value);
      if (tryAutoSelectExactMatch(input, input.value.trim(), lista, row)) {
        fecharSugestoes();
        return;
      }
    }

    if (e.key === "Escape") {
      fecharSugestoes();
    }
  });
}

function abrirSugestoes(input, lista, callback) {
  fecharSugestoes();

  const box = document.createElement("div");
  box.className = "suggestions-box";

  if (!lista.length) {
    const d = document.createElement("div");
    d.className = "suggestion-item no-match";
    d.innerText = "Nenhum resultado";
    box.appendChild(d);
  } else {
    lista.forEach(item => {
      const el = document.createElement("div");
      el.className = "suggestion-item";
      el.textContent = item;
      el.onclick = () => callback(item);
      box.appendChild(el);
    });
  }

  document.body.appendChild(box);
  posicionarBox(input, box);
}

function posicionarBox(input, box) {
  const r = input.getBoundingClientRect();
  box.style.left = r.left + "px";
  box.style.top = r.bottom + "px";
  box.style.width = r.width + "px";
  box.style.position = "fixed";
}

function fecharSugestoes() {
  document.querySelectorAll(".suggestions-box").forEach(b => b.remove());
}

function destacar(itens, idx) {
  itens.forEach(i => i.classList.remove("active-sel"));
  if (itens[idx]) itens[idx].classList.add("active-sel");
}

document.addEventListener("click", e => {
  if (!e.target.classList.contains("suggestion-item")) fecharSugestoes();
});
