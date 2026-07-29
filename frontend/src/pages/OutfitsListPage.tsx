import { useState, useEffect, useCallback } from "react";
import { Link, useNavigate } from "react-router-dom";
import * as api from "../api/client";
import type { OutfitResponse } from "../api/client";
import Toast from "../components/Toast";
import "./OutfitsListPage.css";

const API_BASE = import.meta.env.VITE_API_URL || "";

export default function OutfitsListPage() {
  const navigate = useNavigate();
  const [outfits, setOutfits] = useState<OutfitResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleteTarget, setDeleteTarget] = useState<OutfitResponse | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [toast, setToast] = useState<{
    message: string;
    variant: "success" | "error" | "info";
  } | null>(null);

  const loadOutfits = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.listOutfits();
      setOutfits(data);
    } catch {
      setToast({
        message: "Outfits konnten nicht geladen werden.",
        variant: "error",
      });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadOutfits();
  }, [loadOutfits]);

  const handleDelete = useCallback(async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await api.deleteOutfit(deleteTarget.id);
      setOutfits((prev) => prev.filter((o) => o.id !== deleteTarget.id));
      setDeleteTarget(null);
      setToast({ message: "Outfit gelöscht.", variant: "success" });
    } catch {
      setToast({
        message: "Outfit konnte nicht gelöscht werden.",
        variant: "error",
      });
    } finally {
      setDeleting(false);
    }
  }, [deleteTarget]);

  return (
    <div className="ol-page">
      <div className="ol-page__header">
        <h1 className="ol-page__title">Gespeicherte Outfits</h1>
        <Link to="/outfits/create" className="btn btn-primary">
          Neues Outfit
        </Link>
      </div>

      {loading && (
        <p className="ol-loading">Outfits werden geladen...</p>
      )}

      {!loading && outfits.length === 0 && (
        <div className="ol-empty">
          <span className="ol-empty__icon">&#9733;</span>
          <h2 className="ol-empty__title">Noch keine Outfits</h2>
          <p className="ol-empty__text">
            Ihre glamourösen Kombinationen erscheinen hier. Starten Sie im Outfit
            Creator und kreieren Sie Ihren ersten Look für den roten Teppich.
          </p>
          <Link to="/outfits/create" className="btn btn-primary">
            Erstes Outfit erstellen
          </Link>
        </div>
      )}

      {!loading && outfits.length > 0 && (
        <div className="ol-grid">
          {outfits.map((outfit) => (
            <article key={outfit.id} className="ol-card">
              <div className="ol-card__thumbnails">
                {outfit.items.length === 0 ? (
                  <div className="ol-card__no-items">
                    Keine Kleidungsstücke
                  </div>
                ) : (
                  outfit.items.slice(0, 3).map((item) => (
                    <div key={item.id} className="ol-card__thumb-wrap">
                      <img
                        src={`${API_BASE}/static/${item.image_path}`}
                        alt={item.name}
                        className="ol-card__thumb-img"
                      />
                    </div>
                  ))
                )}
                {outfit.items.length > 3 && (
                  <div className="ol-card__thumb-wrap ol-card__thumb--more">
                    <span className="ol-card__thumb-more">
                      +{outfit.items.length - 3}
                    </span>
                  </div>
                )}
              </div>
              <div className="ol-card__body">
                <h3 className="ol-card__name">{outfit.name}</h3>
                <p className="ol-card__count">
                  {outfit.items.length}{" "}
                  {outfit.items.length === 1 ? "Teil" : "Teile"}
                </p>
              </div>
              <div className="ol-card__actions">
                <button
                  type="button"
                  className="btn btn-secondary ol-card__btn"
                  onClick={() =>
                    navigate(`/outfits/create?edit=${outfit.id}`)
                  }
                >
                  Bearbeiten
                </button>
                <button
                  type="button"
                  className="btn ol-card__btn ol-card__btn--danger"
                  onClick={() => setDeleteTarget(outfit)}
                >
                  Löschen
                </button>
              </div>
            </article>
          ))}
        </div>
      )}

      {deleteTarget && (
        <div
          className="ol-dialog-overlay"
          onClick={() => setDeleteTarget(null)}
          role="dialog"
          aria-modal="true"
        >
          <div
            className="ol-dialog"
            onClick={(e) => e.stopPropagation()}
          >
            <h2 className="ol-dialog__title">Outfit löschen</h2>
            <p className="ol-dialog__text">
              Möchten Sie das Outfit &bdquo;{deleteTarget.name}&rdquo;
              wirklich löschen? Diese Aktion kann nicht rückgängig gemacht
              werden.
            </p>
            <div className="ol-dialog__actions">
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
                className="btn ol-dialog__delete-btn"
                onClick={handleDelete}
                disabled={deleting}
              >
                {deleting ? "Löscht..." : "Löschen"}
              </button>
            </div>
          </div>
        </div>
      )}

      {toast && (
        <Toast
          variant={toast.variant}
          onClose={() => setToast(null)}
        >
          {toast.message}
        </Toast>
      )}
    </div>
  );
}
