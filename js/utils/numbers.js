export function parseBrazilNumber(str) {
  if (str === null || str === undefined || str === "") return 0;
  let s = String(str).trim();
  if (s.indexOf(",") > -1 && s.indexOf(".") > -1)
    s = s.replace(/\./g, '').replace(/,/g, '.');
  else if (s.indexOf(",") > -1)
    s = s.replace(/,/g, '.');

  const v = parseFloat(s);
  return isNaN(v) ? 0 : v;
}

export function formatBrazilNumber(n) {
  if (n === null || n === undefined || n === "") return "";
  return new Intl.NumberFormat("pt-BR", {
    maximumFractionDigits: 2,
    minimumFractionDigits: 0
  }).format(Number(n));
}

export function safeDiv(a, b) {
  const na = parseBrazilNumber(a);
  const nb = parseBrazilNumber(b);
  if (nb === 0) return 0;
  return na / nb;
}
