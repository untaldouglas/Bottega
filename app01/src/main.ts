import {
  createIdea,
  sortIdeas,
  updateIdea,
  STATES,
  type Idea,
  type Estado,
  type Score,
} from "./domain";
import {
  exportDocument,
  importPreview,
  applyImport,
  type ImportMode,
} from "./exchange";
import {
  IndexedDbCollectionRepository,
  type CollectionRepository,
} from "./repository";

const repo: CollectionRepository = new IndexedDbCollectionRepository();
let ideas: Idea[] = [];
let deleted: { idea: Idea; timer: number } | undefined;
let editingId: string | null = null;
let visibleLimit = 200;
const root = document.querySelector<HTMLDivElement>("#app")!;
const make = <K extends keyof HTMLElementTagNameMap>(tag: K, text?: string) => {
  const element = document.createElement(tag);
  if (text !== undefined) element.textContent = text;
  return element;
};
const value = (form: HTMLFormElement, name: string) =>
  String(new FormData(form).get(name) ?? "");
function setStatus(message: string) {
  const status = document.querySelector<HTMLElement>("#status");
  if (status) status.textContent = message;
}
function inputField(
  labelText: string,
  name: string,
  type: string,
  current = "",
) {
  const label = make("label");
  label.append(make("span", labelText));
  const input = type === "textarea" ? make("textarea") : make("input");
  input.name = name;
  if (type !== "textarea") (input as HTMLInputElement).type = type;
  if (current)
    (input as HTMLInputElement | HTMLTextAreaElement).value = current;
  if (/titulo|descripcion/i.test(name)) input.required = true;
  if (/titulo/i.test(name)) input.maxLength = 120;
  if (/descripcion/i.test(name)) input.maxLength = 2000;
  if (/impacto|confianza|facilidad/i.test(name)) {
    const numeric = input as HTMLInputElement;
    numeric.min = "1";
    numeric.max = "10";
    numeric.step = "1";
    numeric.required = true;
    numeric.inputMode = "numeric";
  }
  label.append(input);
  return label;
}
function closeDialog(dialog: HTMLDialogElement, trigger?: HTMLElement) {
  if (dialog.open) dialog.close();
  dialog.remove();
  trigger?.focus();
}
function enhanceDialog(
  dialog: HTMLDialogElement,
  trigger: HTMLElement,
  initial: HTMLElement,
) {
  dialog.addEventListener("cancel", (event) => {
    event.preventDefault();
    closeDialog(dialog, trigger);
  });
  dialog.addEventListener("keydown", (event) => {
    if (event.key !== "Tab") return;
    const focusable = Array.from(
      dialog.querySelectorAll<HTMLElement>(
        "button, select, input, textarea, [tabindex]:not([tabindex='-1'])",
      ),
    );
    if (!focusable.length) return;
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  });
  dialog.addEventListener("close", () => trigger.focus(), { once: true });
  dialog.showModal();
  initial.focus();
}
function openDeleteDialog(idea: Idea, trigger: HTMLElement) {
  const dialog = make("dialog") as HTMLDialogElement;
  dialog.className = "dialog";
  dialog.setAttribute("aria-labelledby", "delete-title");
  const title = make("h2", "Confirmar eliminación");
  title.id = "delete-title";
  const message = make(
    "p",
    `¿Eliminar “${idea.titulo}”? Puedes deshacer durante 10 segundos.`,
  );
  const actions = make("div");
  actions.className = "dialog-actions";
  const cancel = make("button", "Cancelar");
  cancel.type = "button";
  const confirm = make("button", "Eliminar idea");
  confirm.type = "button";
  confirm.className = "danger";
  cancel.onclick = () => closeDialog(dialog, trigger);
  confirm.onclick = async () => {
    closeDialog(dialog, trigger);
    deleted = {
      idea,
      timer: window.setTimeout(() => {
        deleted = undefined;
        render();
        setStatus(
          "La ventana de deshacer expiró; la eliminación es definitiva.",
        );
      }, 10000),
    };
    await commit(ideas.filter((item) => item.id !== idea.id));
    setStatus("Idea eliminada. Puedes deshacer durante 10 segundos.");
  };
  actions.append(cancel, confirm);
  dialog.append(title, message, actions);
  document.body.append(dialog);
  enhanceDialog(dialog, trigger, confirm);
}
function openImportDialog(text: string, file: File, trigger: HTMLElement) {
  const dialog = make("dialog") as HTMLDialogElement;
  dialog.className = "dialog";
  dialog.setAttribute("aria-labelledby", "import-title");
  const title = make("h2", "Vista previa de importación");
  title.id = "import-title";
  const summary = make("p");
  summary.setAttribute("aria-live", "polite");
  summary.setAttribute("aria-atomic", "true");
  const modeLabel = make("label", "Modo de importación");
  const mode = make("select") as HTMLSelectElement;
  mode.id = "import-mode";
  mode.name = "import-mode";
  mode.append(
    new Option("Combinar", "combinar"),
    new Option("Reemplazar", "reemplazar"),
  );
  modeLabel.append(mode);
  const errors = make("p");
  errors.className = "error";
  const actions = make("div");
  actions.className = "dialog-actions";
  const cancel = make("button", "Cancelar");
  cancel.type = "button";
  const confirm = make("button", "Confirmar importación");
  confirm.type = "button";
  const close = make("button", "Cerrar");
  close.type = "button";
  close.className = "secondary";
  let current = importPreview(text, ideas, "combinar", file.size);
  const refresh = () => {
    current = importPreview(text, ideas, mode.value as ImportMode, file.size);
    summary.textContent = `Archivo ${file.name}: ${current.incomingCount} ideas, ${current.conflicts.length} conflictos, ${current.issues.length} errores.`;
    errors.textContent = current.issues.length
      ? `Importación rechazada: ${current.issues.map((issue) => issue.message).join("; ")}`
      : "Sin errores. La colección no cambia hasta confirmar.";
    confirm.disabled = current.issues.length > 0;
    confirm.hidden = current.issues.length > 0;
    cancel.hidden = current.issues.length > 0;
    close.hidden = current.issues.length === 0;
  };
  mode.onchange = refresh;
  cancel.onclick = () => {
    inputReset();
    closeDialog(dialog, trigger);
  };
  close.onclick = () => {
    inputReset();
    closeDialog(dialog, trigger);
  };
  confirm.onclick = async () => {
    await commit(
      applyImport(current, ideas),
      mode.value === "combinar"
        ? "Importación combinada: colección actualizada sin duplicados."
        : "Importación reemplazada: colección actualizada.",
    );
    inputReset();
    closeDialog(dialog, trigger);
  };
  actions.append(cancel, close, confirm);
  dialog.append(title, summary, modeLabel, errors, actions);
  document.body.append(dialog);
  refresh();
  enhanceDialog(dialog, trigger, current.issues.length ? close : mode);
  function inputReset() {
    const input = document.querySelector<HTMLInputElement>("#import");
    if (input) input.value = "";
  }
}
function editor(idea?: Idea): HTMLFormElement {
  const form = make("form") as HTMLFormElement;
  form.className = "card editor";
  if (idea) form.classList.add("edit-form");
  const prefix = idea ? "edit" : "";
  const name = (base: string) =>
    prefix ? `${prefix}${base[0].toUpperCase()}${base.slice(1)}` : base;
  form.append(
    make("h2", idea ? "Editar idea" : "Nueva idea"),
    make(
      "p",
      "Prioridad = impacto × confianza × facilidad. Cada criterio acepta un número entero de 1 a 10.",
    ),
  );
  const grid = make("div");
  grid.className = "grid";
  grid.append(
    inputField(
      idea ? "Editar título" : "Título",
      name("titulo"),
      "text",
      idea?.titulo,
    ),
    inputField(
      idea ? "Editar impacto" : "Impacto",
      name("impacto"),
      "number",
      idea ? String(idea.impacto) : "",
    ),
    inputField(
      idea ? "Editar confianza" : "Confianza",
      name("confianza"),
      "number",
      idea ? String(idea.confianza) : "",
    ),
    inputField(
      idea ? "Editar facilidad" : "Facilidad",
      name("facilidad"),
      "number",
      idea ? String(idea.facilidad) : "",
    ),
  );
  form.append(
    grid,
    inputField(
      idea ? "Editar descripción" : "Descripción",
      name("descripcion"),
      "textarea",
      idea?.descripcion,
    ),
    inputField(
      idea
        ? "Editar etiquetas (separadas por coma)"
        : "Etiquetas (separadas por coma)",
      name("etiquetas"),
      "text",
      idea?.etiquetas.join(", "),
    ),
    inputField(
      idea ? "Editar notas" : "Notas",
      name("notas"),
      "textarea",
      idea?.notas,
    ),
  );
  const actions = make("div");
  actions.className = "controls";
  const save = make("button", idea ? "Guardar cambios" : "Agregar idea");
  save.type = "submit";
  const cancel = make("button", "Cancelar");
  cancel.type = "button";
  cancel.className = "secondary";
  cancel.onclick = () => {
    editingId = null;
    render();
  };
  actions.append(save, cancel);
  form.append(actions);
  form.onsubmit = async (event) => {
    event.preventDefault();
    const scores = [
      Number(value(form, name("impacto"))),
      Number(value(form, name("confianza"))),
      Number(value(form, name("facilidad"))),
    ];
    if (
      scores.some(
        (score) => !Number.isInteger(score) || score < 1 || score > 10,
      )
    ) {
      setStatus(
        "No se aplicó ningún cambio. Cada criterio debe ser un número entero de 1 a 10.",
      );
      return;
    }
    const editable = {
      titulo: value(form, name("titulo")),
      descripcion: value(form, name("descripcion")),
      impacto: scores[0] as Score,
      confianza: scores[1] as Score,
      facilidad: scores[2] as Score,
      etiquetas: value(form, name("etiquetas"))
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean),
      notas: value(form, name("notas")),
    };
    const next = idea
      ? ideas.map((item) =>
          item.id === idea.id
            ? updateIdea(idea, editable, new Date().toISOString())
            : item,
        )
      : [
          ...ideas,
          createIdea(editable, {
            id: () => crypto.randomUUID(),
            now: () => new Date().toISOString(),
          }),
        ];
    editingId = null;
    await commit(
      next,
      idea
        ? "Idea actualizada; la prioridad se recalculó."
        : "Idea creada y guardada en la colección local.",
    );
  };
  return form;
}
function scrollTo(element: Element) {
  element.scrollIntoView({
    behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches
      ? "auto"
      : "smooth",
  });
}
function render() {
  root.replaceChildren();
  const app = make("div");
  app.className = "shell";
  const skip = make("a", "Saltar al contenido");
  skip.className = "skip-link";
  skip.href = "#main-content";
  const header = make("header");
  header.className = "hero";
  const eyebrow = make("p", "HALLMARK / COLECCIÓN LOCAL");
  eyebrow.className = "eyebrow";
  header.append(
    eyebrow,
    make("h1", "Idea Prioritizer"),
    make(
      "p",
      "Registra ideas, haz explícita su prioridad y conserva el control de tu colección local.",
    ),
  );
  const nav = make("nav");
  nav.setAttribute("aria-label", "Secciones");
  const newButton = make("button", "Nueva idea");
  newButton.type = "button";
  newButton.onclick = () => {
    const editorElement = document.querySelector(".editor");
    if (editorElement) scrollTo(editorElement);
    document.querySelector<HTMLInputElement>(".editor input")?.focus();
  };
  const listButton = make("button", "Ver colección");
  listButton.type = "button";
  listButton.className = "secondary";
  listButton.onclick = () => {
    const collectionElement = document.querySelector("#collection");
    if (collectionElement) scrollTo(collectionElement);
  };
  nav.append(newButton, listButton);
  header.append(nav);
  app.append(skip, header);
  const main = make("main");
  main.id = "main-content";
  const status = make("div");
  status.id = "status";
  status.className = "live-region";
  status.setAttribute("role", "status");
  status.setAttribute("aria-live", "polite");
  status.setAttribute("aria-atomic", "true");
  main.append(status, editor());
  const exchange = make("section");
  exchange.className = "card exchange";
  exchange.setAttribute("aria-labelledby", "exchange-title");
  const exchangeTitle = make("h2", "Importar y exportar");
  exchangeTitle.id = "exchange-title";
  exchange.append(
    exchangeTitle,
    make(
      "p",
      "La colección no cambia hasta confirmar. Combinar es el modo predeterminado; Reemplazar es explícito.",
    ),
  );
  const actions = make("div");
  actions.className = "controls";
  const exportButton = make("button", "Exportar JSON");
  exportButton.type = "button";
  exportButton.onclick = () => download(exportDocument(ideas), "ideas.json");
  const label = make("label", "Seleccionar JSON para importar");
  label.className = "file-button";
  const input = make("input") as HTMLInputElement;
  input.id = "import";
  input.type = "file";
  input.accept = "application/json";
  label.append(input);
  input.onchange = async () => {
    const file = input.files?.[0];
    if (!file) return;
    try {
      openImportDialog(await file.text(), file, input);
    } catch {
      setStatus(
        "Importación rechazada: no fue posible leer el archivo seleccionado.",
      );
      input.value = "";
    }
  };
  actions.append(exportButton, label);
  exchange.append(actions);
  main.append(exchange);
  const collection = make("section");
  collection.id = "collection";
  collection.setAttribute("aria-labelledby", "collection-title");
  const collectionTitle = make("h2", "Tu colección");
  collectionTitle.id = "collection-title";
  collection.append(
    collectionTitle,
    make(
      "p",
      ideas.length
        ? `${ideas.length} ideas guardadas localmente.`
        : "Aún no hay ideas. Crea la primera para comenzar.",
    ),
  );
  const list = make("ul");
  list.className = "ideas";
  for (const idea of sortIdeas(ideas).slice(0, visibleLimit)) {
    const item = make("li");
    item.className = "idea-card idea";
    if (editingId === idea.id) {
      item.append(editor(idea));
      list.append(item);
      continue;
    }
    const title = make("h3", idea.titulo);
    const description = make("p", idea.descripcion);
    const meta = make(
      "p",
      `Prioridad ${idea.prioridad} · ${idea.estado} · ${idea.impacto}/${idea.confianza}/${idea.facilidad}`,
    );
    meta.className = "meta";
    const controls = make("div");
    controls.className = "controls";
    const state = make("select") as HTMLSelectElement;
    state.setAttribute("aria-label", `Estado de ${idea.titulo}`);
    for (const stateValue of STATES)
      state.add(
        new Option(
          stateValue,
          stateValue,
          stateValue === idea.estado,
          stateValue === idea.estado,
        ),
      );
    state.onchange = () =>
      void commit(
        ideas.map((item) =>
          item.id === idea.id
            ? {
                ...item,
                estado: state.value as Estado,
                modificadaEn: new Date().toISOString(),
              }
            : item,
        ),
        "Estado actualizado en la colección local.",
      );
    const edit = make("button", "Editar");
    edit.type = "button";
    edit.className = "secondary";
    edit.onclick = () => {
      editingId = idea.id;
      render();
      document.querySelector<HTMLInputElement>(".edit-form input")?.focus();
    };
    const remove = make("button", "Eliminar");
    remove.type = "button";
    remove.className = "danger";
    remove.onclick = () => openDeleteDialog(idea, remove);
    controls.append(state, edit, remove);
    item.append(title, description, meta, controls);
    list.append(item);
  }
  collection.append(list);
  if (ideas.length > visibleLimit) {
    const more = make(
      "button",
      `Mostrar más (${ideas.length - visibleLimit} restantes)`,
    );
    more.type = "button";
    more.className = "secondary";
    more.onclick = () => {
      visibleLimit += 200;
      render();
      more.focus();
    };
    collection.append(more);
  }
  main.append(collection);
  if (deleted) {
    const undo = make("button", "Deshacer eliminación");
    undo.type = "button";
    undo.className = "undo";
    undo.onclick = () => {
      window.clearTimeout(deleted!.timer);
      const restored = deleted!.idea;
      deleted = undefined;
      void commit(
        [...ideas, restored],
        "Eliminación deshecha: idea restaurada en la colección local.",
      );
      setStatus("Idea restaurada en la colección local.");
    };
    main.append(undo);
  }
  app.append(main);
  root.append(app);
}
async function commit(
  next: Idea[],
  successMessage = "Colección local actualizada.",
) {
  const result = await repo.commit(next);
  if (!result.ok) {
    setStatus(
      `No se aplicó ningún cambio. ${result.issues.map((issue) => issue.message).join("; ")}`,
    );
    return;
  }
  ideas = sortIdeas(next);
  render();
  setStatus(successMessage);
}
function download(json: string, name: string) {
  const anchor = make("a") as HTMLAnchorElement;
  anchor.href = URL.createObjectURL(
    new Blob([json], { type: "application/json" }),
  );
  anchor.download = name;
  anchor.click();
  URL.revokeObjectURL(anchor.href);
}
void repo.load().then((result) => {
  if (result.ok) {
    ideas = result.value;
    render();
  } else {
    render();
    setStatus(
      "Persistencia local no disponible o temporal; exporta respaldos y reintenta.",
    );
  }
});
