import { useState, useEffect, useCallback } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import * as api from "../api/client";
import type { ClothingItemResponse, OutfitResponse } from "../api/client";
import OutfitPreview from "../components/OutfitPreview";
import Toast from "../components/Toast";
import "./OutfitCreatorPage.css";

const CATEGORIES = ["Oberteile", "Hosen", "Kleider", "Schuhe", "Accessoires"] as const;

export default function OutfitCreatorPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const editId = searchParams.get("edit");

  const [outfitName, setOutfitName] = useState("");
  const [selectedByCategory, setSelectedByCategory] = useState<
    Record<string, ClothingItemResponse>
  >({});
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(
    new Set(["Oberteile"])
  );
  const [categoryItems, setCategoryItems] = useState<
    Record<string, ClothingItemResponse[]>
  >({});
  const [loadingCategories, setLoadingCategories] = useState<Set<string>>(
    new Set()
  );
  const [saving, setSaving] = useState(false);
  const [toast, setToast] = useState<{
    message: string;
    variant: "success" | "error" | "info";
  } | null>(null);

  useEffect(() => {
    if (editId) {
      const id = parseInt(editId, 10);
      if (!isNaN(id)) {
        api
          .getOutfit(id)
          .then((outfit: OutfitResponse) => {
            setOutfitName(outfit.name);
            const selected: Record<string, ClothingItemResponse> = {};
            for (const item of outfit.items) {
              selected[item.category] = item;
            }
            setSelectedByCategory(selected);
            const catsToExpand = new Set<string>();
            for (const item of outfit.items) {
              catsToExpand.add(item.category);
            }
            setExpandedCategories(catsToExpand);
          })
          .catch(() => {
            setToast({
              message: "Outfit konnte nicht geladen werden.",
              variant: "error",
            });
          });
      }
    }
  }, [editId]);

  const loadCategory = useCallback(async (category: string) => {
    setLoadingCategories((prev) => new Set(prev).add(category));
    try {
      const items = await api.listItems(category);
      setCategoryItems((prev) => ({ ...prev, [category]: items }));
    } catch {
      setToast({
        message: `Kategorie "${category}" konnte nicht geladen werden.`,
        variant: "error",
      });
    } finally {
      setLoadingCategories((prev) => {
        const next = new Set(prev);
        next.delete(category);
        return next;
      });
    }
  }, []);

  const toggleCategory = useCallback(
    (category: string) => {
      setExpandedCategories((prev) => {
        const next = new Set(prev);
        if (next.has(category)) {
          next.delete(category);
        } else {
          next.add(category);
          if (!categoryItems[category]) {
            loadCategory(category);
          }
        }
        return next;
      });
    },
    [categoryItems, loadCategory]
  );

  const selectItem = useCallback(
    (category: string, item: ClothingItemResponse) => {
      setSelectedByCategory((prev) => ({
        ...prev,
        [category]: item,
      }));
    },
    []
  );

  const removeItem = useCallback((category: string) => {
    setSelectedByCategory((prev) => {
      const next = { ...prev };
      delete next[category];
      return next;
    });
  }, []);

  const selectedItems = Object.values(selectedByCategory);

  const handleSave = useCallback(async () => {
    if (!outfitName.trim()) {
      setToast({
        message: "Bitte geben Sie Ihrem Outfit einen Namen.",
        variant: "error",
      });
      return;
    }
    if (selectedItems.length < 2) {
      setToast({
        message: "Wählen Sie mindestens zwei Kleidungsstücke aus.",
        variant: "error",
      });
      return;
    }

    setSaving(true);
    try {
      const itemIds = selectedItems.map((item) => item.id);
      if (editId) {
        await api.updateOutfit(parseInt(editId, 10), {
          name: outfitName.trim(),
          clothing_item_ids: itemIds,
        });
        setToast({ message: "Outfit aktualisiert!", variant: "success" });
      } else {
        await api.createOutfit({
          name: outfitName.trim(),
          clothing_item_ids: itemIds,
        });
        setToast({ message: "Outfit gespeichert!", variant: "success" });
      }
      setTimeout(() => navigate("/outfits"), 1200);
    } catch (err) {
      setToast({
        message:
          err instanceof Error ? err.message : "Fehler beim Speichern des Outfits.",
        variant: "error",
      });
    } finally {
      setSaving(false);
    }
  }, [outfitName, selectedItems, editId, navigate]);

  return (
    <div className="oc-page">
      <h1 className="oc-page__title">
        {editId ? "Outfit bearbeiten" : "Outfit Creator"}
      </h1>

      <div className="oc-layout">
        <aside className="oc-sidebar">
          {CATEGORIES.map((category) => {
            const isExpanded = expandedCategories.has(category);
            const isLoading = loadingCategories.has(category);
            const items = categoryItems[category] || [];
            const selected = selectedByCategory[category];

            return (
              <div
                key={category}
                className={`oc-accordion ${isExpanded ? "oc-accordion--open" : ""}`}
              >
                <button
                  type="button"
                  className="oc-accordion__header"
                  onClick={() => toggleCategory(category)}
                  aria-expanded={isExpanded}
                >
                  <span className="oc-accordion__title">{category}</span>
                  <span className="oc-accordion__chevron">&#9662;</span>
                </button>
                {isExpanded && (
                  <div className="oc-accordion__body">
                    {isLoading && (
                      <p className="oc-accordion__loading">Laden...</p>
                    )}
                    {!isLoading && items.length === 0 && (
                      <p className="oc-accordion__empty">
                        Keine Kleidungsstücke in dieser Kategorie.
                      </p>
                    )}
                    {!isLoading && (
                      <div className="oc-item-grid">
                        {items.map((item) => (
                          <button
                            key={item.id}
                            type="button"
                            className={`oc-item-thumb ${selected?.id === item.id ? "oc-item-thumb--selected" : ""}`}
                            onClick={() => selectItem(category, item)}
                            title={item.name}
                          >
                            <div className="oc-item-thumb__img-wrap">
                              <img
                                src={`${import.meta.env.VITE_API_URL || ""}/static/${item.image_path}`}
                                alt={item.name}
                                className="oc-item-thumb__img"
                              />
                            </div>
                            <span className="oc-item-thumb__name">
                              {item.name}
                            </span>
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </aside>

        <section className="oc-preview-panel">
          <h2 className="oc-preview-panel__heading">Ihr Outfit</h2>
          <OutfitPreview items={selectedItems} onRemove={removeItem} />

          <div className="oc-save-area">
            <div className="oc-save-area__field">
              <label htmlFor="outfit-name" className="oc-save-area__label">
                Outfit-Name
              </label>
              <input
                id="outfit-name"
                type="text"
                className="oc-save-area__input"
                placeholder="z.B. Abend-Gala, Casual Friday..."
                value={outfitName}
                onChange={(e) => setOutfitName(e.target.value)}
              />
            </div>
            <button
              type="button"
              className="btn btn-primary oc-save-btn"
              onClick={handleSave}
              disabled={saving}
            >
              {saving
                ? "Speichert..."
                : editId
                  ? "Outfit aktualisieren"
                  : "Outfit speichern"}
            </button>
          </div>
        </section>
      </div>

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
