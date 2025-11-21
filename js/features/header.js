export function inicializarHeaderCorporativo() {
  const header = document.querySelector(".header-corp");
  if (!header) return;

  window.addEventListener("scroll", () => {
    if (window.scrollY > 10) header.classList.add("header-small");
    else header.classList.remove("header-small");
  });
}
