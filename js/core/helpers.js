export function getElementByMultiIds(...ids) {
  for (const id of ids) {
    const el = document.getElementById(id);
    if (el) return el;
  }
  return null;
}

export function getInputByNameOrIds(name, ...ids) {
  return (
    document.querySelector(`input[name="${name}"]`) ||
    getElementByMultiIds(...ids) ||
    null
  );
}
