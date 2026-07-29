import { useState, useEffect, useCallback, useRef, type ChangeEvent, type FormEvent } from "react";
import * as api from "../api/client";
import type { ClothingItemResponse } from "../api/client";
import Toast from "../components/Toast";
import "./WardrobePage.css";

const API_BASE = import.meta.env.VITE_API_URL || "";

const CATEGORIES = ["Oberteile", "Hosen", "Kleider", "Schuhe", "Accessoires"] as const;

export default function WardrobePage() {
  const [items, setItems] = useState<ClothingItemResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string>("");
  const [toast, setToast] = useState<{
    message: string;
    variant: "success" | "error" | "info";
  } | null>(null);

  const [showAddModal, setShowAddModal] = useState(false);
  const [editingItem, setEditingItem] = useState<ClothingItemResponse | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<ClothingItemResponse | null>(null);
  const [deleting, setDeleting] = useState(false);

  const [formName, setFormName] = useState("");
  const [formCategory, setFormCategory] = useState("Oberteile");
  const [formNote, setFormNote] = useState("");
  const [formFile, setFormFile] = useState<File | null>(null);
  const [formError, setFormError] = useState("");
  const [formSubmitting, setFormSubmitting] = useState(false);
  const [imagePreview, setImagePreview] = useState<string>("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadItems = useCallback(async (category?: string) => {
    setLoading(true);
    try {
      const data = await api.listItems(category || undefined);
      setItems(data);
    } catch {
      setToast({
        message: "Garderobe konnte nicht geladen werden.",
        variant: "error",
      });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadItems(selectedCategory || undefined);
  }, [selectedCategory, loadItems]);

  const handleCategoryChange = useCallback((category: string) => {
    setSelectedCategory(category);
  }, []);

  const openAddModal = useCallback(() => {
    setEditingItem(null);
    setFormName("");
    setFormCategory("Oberteile");
    setFormNote("");
    setFormFile(null);
    setFormError("");
    setImagePreview("");
    setShowAddModal(true);
  }, []);

  const openEditModal = useCallback((item: ClothingItemResponse) => {
    setEditingItem(item);
    setFormName(item.name);
    setFormCategory(item.category);
    setFormNote(item.note || "");
    setFormFile(null);
    setFormError("");
    setImagePreview(`${API_BASE}/static/${item.image_path}`);
    setShowAddModal(true);
  }, []);

  const closeModal = useCallback(() => {
    setShowAddModal(false);
    setEditingItem(null);
    if (imagePreview && !editingItem) {
      URL.revokeObjectURL(imagePreview);
    }
    setImagePreview("");
  }, [imagePreview, editingItem]);

  const handleFileChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (!file) return;
      const validTypes = ["image/jpeg", "image/png"];
      if (!validTypes.includes(file.type)) {
        setFormError("Nur JPEG- und PNG-Bilder sind erlaubt.");
        return;
      }
      if (file.size > 5 * 1024 * 1024) {
        setFormError("Bild darf maximal 5 MB gro\u00df sein.");
        return;
      }
      if (imagePreview && !editingItem) {
        URL.revokeObjectURL(imagePreview);
      }
      setFormFile(file);
      setFormError("");
      setImagePreview(URL.createObjectURL(file));
    },
    [imagePreview, editingItem]
  );

  const handleFormSubmit = useCallback(
    async (e: FormEvent) => {
      e.preventDefault();
      setFormError("");

      if (!formName.trim()) {
        setFormError("Bitte geben Sie einen Namen ein.");
        return;
      }

      if (editingItem ? !imagePreview : !formFile) {
        setFormError("Bitte laden Sie ein Bild hoch.");
        return;
      }

      setFormSubmitting(true);
      try {
        const fd = new FormData();
        fd.append("name", formName.trim());
        fd.append("category", formCategory);
        if (formNote.trim()) {
          fd.append("note", formNote.trim());
        }
        if (formFile) {
          fd.append("image", formFile);
        }

        if (editingItem) {
          const updated = await api.updateItem(editingItem.id, fd);
          setItems((prev) =>
            prev.map((it) => (it.id === updated.id ? updated : it))
          );
          setToast({ message: "Kleidungsst\u00fcck aktualisiert.", variant: "success" });
        } else {
          const created = await api.createItem(fd);
          setItems((prev) => [created, ...prev]);
          setToast({ message: "Kleidungsst\u00fcck hinzugef\u00fcgt.", variant: "success" });
        }
        closeModal();
      } catch (err) {
        setFormError(
          err instanceof Error ? err.message : "Fehler beim Speichern."
        );
      } finally {
        setFormSubmitting(false);
      }
    },
    [formName, formCategory, formNote, formFile, imagePreview, editingItem, closeModal]
  );

  const handleDelete = useCallback(async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await api.deleteItem(deleteTarget.id);
      setItems((prev) => prev.filter((it) => it.id !== deleteTarget.id));
      setDeleteTarget(null);
      setToast({ message: "Kleidungsst\u00fcck gel\u00f6scht.", variant: "success" });
    } catch {
      setToast({
        message: "Kleidungsst\u00fcck konnte nicht gel\u00f6scht werden.",
        variant: "error",
      });
    } finally {
      setDeleting(false);
    }
  }, [deleteTarget]);

  return (
    <div className="wp-page">
      <div className="wp-page__header">
        <h1 className="wp-page__title">Garderobe</h1>
        <button type="button" className="btn btn-primary" onClick={openAddModal}>
          Neues Kleidungsst\u00fcck
        </button>
      </div>

      <div className="wp-tabs">
        <button
          type="button"
          className={`wp-tab${selectedCategory === "" ? " wp-tab--active" : ""}`}
          onClick={() => handleCategoryChange("")}
        >
          Alle
        </button>
        {CATEGORIES.map((cat) => (
          <button
            key={cat}
            type="button"
            className={`wp-tab${selectedCategory === cat ? " wp-tab--active" : ""}`}
            onClick={() => handleCategoryChange(cat)}
          >
            {cat}
          </button>
        ))}
      </div>

      {loading && <p className="wp-loading">Garderobe wird geladen...</p>}

      {!loading && items.length === 0 && (
        <div className="wp-empty">
          <span className="wp-empty__icon">&#9733;</span>
          <h2 className="wp-empty__title">
            {selectedCategory
              ? `Keine ${selectedCategory}`
              : "Ihre Garderobe ist leer"}
          </h2>
          <p className="wp-empty__text">
            {selectedCategory
              ? `Sie haben noch keine Kleidungsst\u00fccke in der Kategorie &bdquo;${selectedCategory}&rdquo;. F\u00fcgen Sie Ihr erstes Teil hinzu.`
              : "Ihre glamour\u00f6se Sammlung erscheint hier. Laden Sie Ihr erstes Kleidungsst\u00fcck hoch und starten Sie Ihre digitale Garderobe."}
          </p>
          <button type="button" className="btn btn-primary" onClick={openAddModal}>
            Erstes Kleidungsst\u00fcck hinzuf\u00fcgen
          </button>
        </div>
      )}

      {!loading && items.length > 0 && (
        <div className="wp-grid">
          {items.map((item) => (
            <article key={item.id} className="wp-card">
              <div className="wp-card__image-wrap">
                <img
                  src={`${API_BASE}/static/${item.image_path}`}
                  alt={item.name}
                  className="wp-card__image"
                  loading="lazy"
                />
              </div>
              <div className="wp-card__body">
                <h3 className="wp-card__name">{item.name}</h3>
                <p className="wp-card__category">{item.category}</p>
                {item.note && <p className="wp-card__note">{item.note}</p>}
              </div>
              <div className="wp-card__actions">
                <button
                  type="button"
                  className="btn btn-secondary wp-card__btn"
                  onClick={() => openEditModal(item)}
                >
                  Bearbeiten
                </button>
                <button
                  type="button"
                  className="btn wp-card__btn wp-card__btn--danger"
                  onClick={() => setDeleteTarget(item)}
                >
                  L\u00f6schen
                </button>
              </div>
            </article>
          ))}
        </div>
      )}

      {showAddModal && (
        <div
          className="wp-overlay"
          onClick={closeModal}
          role="dialog"
          aria-modal="true"
        >
          <div className="wp-modal" onClick={(e) => e.stopPropagation()}>
            <h2 className="wp-modal__title">
              {editingItem
                ? "Kleidungsst\u00fcck bearbeiten"
                : "Neues Kleidungsst\u00fcck"}
            </h2>
            <form onSubmit={handleFormSubmit} className="wp-form">
              <label className="wp-form__label">
                Name
                <input
                  type="text"
                  className="wp-form__input"
                  value={formName}
                  onChange={(e) => setFormName(e.target.value)}
                  required
                  maxLength={100}
                  placeholder="z.B. Schwarze Seidenbluse"
                />
              </label>

              <label className="wp-form__label">
                Kategorie
                <select
                  className="wp-form__select"
                  value={formCategory}
                  onChange={(e) => setFormCategory(e.target.value)}
                >
                  {CATEGORIES.map((cat) => (
                    <option key={cat} value={cat}>
                      {cat}
                    </option>
                  ))}
                </select>
              </label>

              <div className="wp-form__label">
                Bild
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/jpeg,image/png"
                  style={{ display: "none" }}
                  onChange={handleFileChange}
                />
                {imagePreview ? (
                  <div className="wp-upload-preview">
                    <img
                      src={imagePreview}
                      alt="Vorschau"
                      className="wp-upload-preview__img"
                    />
                    <button
                      type="button"
                      className="wp-upload-preview__change"
                      onClick={() => fileInputRef.current?.click()}
                    >
                      Bild \u00e4ndern
                    </button>
                  </div>
                ) : (
                  <div
                    className="wp-upload-zone"
                    onClick={() => fileInputRef.current?.click()}
                  >
                    <span className="wp-upload-zone__icon">&#128247;</span>
                    <span className="wp-upload-zone__text">
                      Klicken oder Bild hierher ziehen
                    </span>
                    <span className="wp-upload-zone__hint">
                      JPEG oder PNG, max. 5 MB
                    </span>
                  </div>
                )}
              </div>

              <label className="wp-form__label">
                Notiz (optional)
                <textarea
                  className="wp-form__textarea"
                  value={formNote}
                  onChange={(e) => setFormNote(e.target.value)}
                  maxLength={2000}
                  placeholder="z.B. Gekauft bei..."
                />
              </label>

              {formError && <div className="wp-error">{formError}</div>}

              <div className="wp-form__actions">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={closeModal}
                  disabled={formSubmitting}
                >
                  Abbrechen
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={formSubmitting}
                >
                  {formSubmitting
                    ? "Speichert..."
                    : editingItem
                      ? "Aktualisieren"
                      : "Hinzuf\u00fcgen"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {deleteTarget && (
        <div
          className="wp-overlay"
          onClick={() => setDeleteTarget(null)}
          role="dialog"
          aria-modal="true"
        >
          <div
            className="wp-modal wp-modal--danger"
            onClick={(e) => e.stopPropagation()}
          >
            <h2 className="wp-modal__title">Kleidungsst\u00fcck l\u00f6schen</h2>
            <p className="wp-modal__text">
              M\u00f6chten Sie &bdquo;{deleteTarget.name}&rdquo; wirklich
              l\u00f6schen? Das Bild wird ebenfalls entfernt. Diese Aktion kann
              nicht r\u00fcckg\u00e4ngig gemacht werden.
            </p>
            <div className="wp-form__actions">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => setDeleteTarget(null)}
                disabled={deleting}
              >
                Abbrechen
              </button>
              <button
                type="button"
                className="wp-modal__delete-btn"
                onClick={handleDelete}
                disabled={deleting}
              >
                {deleting ? "L\u00f6scht..." : "L\u00f6schen"}
              </button>
            </div>
          </div>
        </div>
      )}

      {toast && (
        <Toast variant={toast.variant} onClose={() => setToast(null)}>
          {toast.message}
        </Toast>
      )}
    </div>
  );
}
