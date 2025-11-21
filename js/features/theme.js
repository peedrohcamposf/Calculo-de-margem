export const THEMES = {
  brasif: {
    "--corp-bg": "#F4F6FA",
    "--corp-card-bg": "#FFFFFF",
    "--corp-primary": "#002856",
    "--corp-primary-light": "#E3ECF8",
    "--corp-secondary": "#00509E",
    "--corp-accent": "#F28C28",
    "--corp-border": "#CDD6E0",
    "--corp-text": "#1A1A1A",
    "--corp-muted": "#6C7A89"
  },
  maxum: {
    "--corp-bg": "#FFFFFF",
    "--corp-card-bg": "#FFFFFF",
    "--corp-primary": "#C8102E",
    "--corp-primary-light": "#F7D7DB",
    "--corp-secondary": "#3A3A3A",
    "--corp-accent": "#E04252",
    "--corp-border": "#D3D3D3",
    "--corp-text": "#1A1A1A",
    "--corp-muted": "#6D6D6D"
  }
};

export function applyThemeByKey(key) {
  const root = document.documentElement;
  const chosen = THEMES[key] ? key : "brasif";

  root.style.transition = "background 0.32s ease, color 0.32s ease";
  Object.entries(THEMES[chosen]).forEach(([varName, value]) => {
    root.style.setProperty(varName, value);
  });

  document.body.classList.remove("theme-brasif", "theme-maxum");
  document.body.classList.add(`theme-${chosen}`);
}

export function initThemeSwitcher() {
  const select = document.getElementById("empresa");
  if (!select) return;

  select.addEventListener("change", () => applyThemeByKey(select.value));
  applyThemeByKey(select.value || "brasif");
}
