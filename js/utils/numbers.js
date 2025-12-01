export function parseBrazilNumber(v) {
  if (v === null || v === undefined) return 0;

  v = String(v).trim();
  if (v === "") return 0;

  // Remove símbolos e espaços
  v = v.replace(/R\$|\%|\s/g, "");

  // 🔹 Caso venha DO JSON (528727.5), aceitar decimal com ponto
  if (/^\d+(\.\d+)?$/.test(v)) {
    return parseFloat(v);
  }

  // 🔹 Caso já esteja em formato BR (528.727,50)
  if (v.includes(",")) {
    v = v.replace(/\./g, "").replace(",", ".");
    return parseFloat(v) || 0;
  }

  // 🔹 Caso venha como inteiro com pontos de milhar (1.234.567)
  if (/^\d+(\.\d{3})+$/.test(v)) {
    v = v.replace(/\./g, "");
    return parseFloat(v);
  }

  // Fallback seguro
  return parseFloat(v.replace(/\./g, "")) || 0;
}

export function formatBrazilNumber(n) {
  if (n === null || n === undefined || n === "") return "0,00";

  const num = Number(n);

  if (isNaN(num)) return "0,00";

  return new Intl.NumberFormat("pt-BR", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(num);
}

export function safeDiv(a, b) {
  const na = parseBrazilNumber(a);
  const nb = parseBrazilNumber(b);
  if (nb === 0) return 0;
  return na / nb;
}
