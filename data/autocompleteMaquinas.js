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
  });

  // Tipo
  autocompleteCampo(tipo, txt => filtrarTipos(marca.value, txt), item => {
    tipo.value = item;
    const marcas = uniq(maquinasDB.filter(m => m.tipo === item).map(m => m.marca));
    if (marcas.length === 1) marca.value = marcas[0];
    modelo.value = "";
    codigo.value = "";
    valor.value = "";
  });

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
  });

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
  });
}

/* ======================================================
   AUTOCOMPLETE VISUAL (usa document.body para o dropdown)
   ====================================================== */

function autocompleteCampo(input, fnLista, onSelect) {
  let selIndex = -1;
  let currentBox = null;

  const handler = debounce(() => {
    if (!input || input.value.trim() === "") {
      fecharSugestoes();
      return;
    }
    const lista = fnLista(input.value);
    abrirSugestoes(input, lista, onSelect);
    selIndex = -1;
  });

  input.addEventListener("input", handler);

  input.addEventListener("keydown", e => {
    const box = currentBox || document.querySelector(".suggestions-box");
    if (!box) return;

    const itens = [...box.querySelectorAll(".suggestion-item")].filter(i => !i.classList.contains("no-match"));
    if (!itens.length) return;

    if (e.key === "ArrowDown") {
      e.preventDefault();
      selIndex = (selIndex + 1) % itens.length;
      destacar(itens, selIndex);
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      selIndex = (selIndex - 1 + itens.length) % itens.length;
      destacar(itens, selIndex);
    } else if (e.key === "Enter") {
      if (selIndex >= 0) {
        e.preventDefault();
        itens[selIndex].click();
      }
    } else if (e.key === "Escape") {
      fecharSugestoes();
    }
  });

  // fecha em scroll/resize para evitar dropdown fora do lugar
  window.addEventListener("scroll", () => fecharSugestoes(), true);
  window.addEventListener("resize", () => fecharSugestoes());
}

function abrirSugestoes(input, lista, onSelect) {
  fecharSugestoes();

  const box = document.createElement("div");
  box.className = "suggestions-box";

  if (!lista.length) {
    const d = document.createElement("div");
    d.className = "suggestion-item no-match";
    d.innerText = "Nenhum resultado";
    box.appendChild(d);
    document.body.appendChild(box);
    posicionarBox(input, box);
    window.__currentSuggestionsBox = box;
    return;
  }

  lista.forEach(item => {
    const el = document.createElement("div");
    el.className = "suggestion-item";
    el.textContent = item;

    el.onclick = () => {
      onSelect(item);
      fecharSugestoes();
    };

    box.appendChild(el);
  });

  document.body.appendChild(box);
  posicionarBox(input, box);
  window.__currentSuggestionsBox = box;
}

function posicionarBox(input, box) {
  const rect = input.getBoundingClientRect();
  box.style.left = Math.round(rect.left) + "px";
  box.style.top = Math.round(rect.bottom) + "px";
  box.style.width = Math.round(rect.width) + "px";
  box.style.maxHeight = "300px";
  box.style.position = "fixed";
}

function fecharSugestoes() {
  document.querySelectorAll(".suggestions-box").forEach(b => b.remove());
  window.__currentSuggestionsBox = null;
}

function destacar(itens, idx) {
  itens.forEach(i => i.classList.remove("active-sel"));
  if (itens[idx]) itens[idx].classList.add("active-sel");
}

document.addEventListener("click", e => {
  if (!e.target.classList.contains("suggestion-item")) fecharSugestoes();
});
