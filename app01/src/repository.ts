import { validateCollectionCapacity, type Idea, type Result } from "./domain";
export interface CollectionRepository {
  load(): Promise<Result<Idea[]>>;
  commit(next: readonly Idea[]): Promise<Result<void>>;
}
export class MemoryRepository implements CollectionRepository {
  private ideas: Idea[] = [];
  failNext = false;
  failNextCode: "STORAGE_UNAVAILABLE" | "QUOTA_EXCEEDED" =
    "STORAGE_UNAVAILABLE";
  async load() {
    return { ok: true as const, value: [...this.ideas] };
  }
  async commit(next: readonly Idea[]) {
    if (this.failNext) {
      this.failNext = false;
      return {
        ok: false as const,
        issues: [
          {
            code: this.failNextCode,
            path: "$",
            message: "No se pudo guardar",
          },
        ],
      };
    }
    const v = validateCollectionCapacity(next);
    if (!v.ok) return v as Result<void>;
    this.ideas = [...v.value];
    return { ok: true as const, value: undefined };
  }
}
export class IndexedDbCollectionRepository implements CollectionRepository {
  constructor(private readonly dbName = "idea-prioritizer") {}
  private open(): Promise<IDBDatabase> {
    return new Promise((resolve, reject) => {
      if (!("indexedDB" in globalThis)) {
        reject(new Error("unavailable"));
        return;
      }
      const req = indexedDB.open(this.dbName, 1);
      req.onupgradeneeded = () => {
        const db = req.result;
        const store = db.objectStoreNames.contains("ideas")
          ? req.transaction!.objectStore("ideas")
          : db.createObjectStore("ideas", { keyPath: "id" });
        if (!store.indexNames.contains("prioridad"))
          store.createIndex("prioridad", "prioridad");
        if (!store.indexNames.contains("modificadaEn"))
          store.createIndex("modificadaEn", "modificadaEn");
        if (!store.indexNames.contains("estado"))
          store.createIndex("estado", "estado");
        if (!db.objectStoreNames.contains("meta"))
          db.createObjectStore("meta", { keyPath: "key" });
      };
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });
  }
  async load(): Promise<Result<Idea[]>> {
    try {
      const db = await this.open();
      const rows = await new Promise<Idea[]>((resolve, reject) => {
        const r = db.transaction("ideas").objectStore("ideas").getAll();
        r.onsuccess = () => resolve(r.result as Idea[]);
        r.onerror = () => reject(r.error);
      });
      db.close();
      return validateCollectionCapacity(rows);
    } catch {
      return {
        ok: false,
        issues: [
          {
            code: "STORAGE_UNAVAILABLE",
            path: "$",
            message: "El almacenamiento local no está disponible",
          },
        ],
      };
    }
  }
  async commit(next: readonly Idea[]): Promise<Result<void>> {
    const valid = validateCollectionCapacity(next);
    if (!valid.ok) return valid as Result<void>;
    try {
      const db = await this.open();
      await new Promise<void>((resolve, reject) => {
        const tx = db.transaction(["ideas", "meta"], "readwrite");
        tx.objectStore("ideas").clear();
        for (const idea of valid.value) tx.objectStore("ideas").put(idea);
        tx.objectStore("meta").put({
          key: "collection",
          formatVersion: 1,
          updatedAt: new Date().toISOString(),
          ideaCount: valid.value.length,
        });
        tx.oncomplete = () => resolve();
        tx.onerror = () => reject(tx.error);
        tx.onabort = () => reject(tx.error ?? new Error("aborted"));
      });
      db.close();
      return { ok: true, value: undefined };
    } catch {
      return {
        ok: false,
        issues: [
          {
            code: "TRANSACTION_ABORTED",
            path: "$",
            message:
              "No se pudo completar el guardado; se conservó la colección previa",
          },
        ],
      };
    }
  }
}
