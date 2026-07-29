import { useState, useEffect } from "react";
import { listItems, type ClothingItemResponse } from "../api/client";
import CategoryFilter from "../components/CategoryFilter";
import WardrobeGrid from "../components/WardrobeGrid";
import "./WardrobePage.css";

const ALL_CATEGORIES = [
  "Alle",
  "Oberteile",
  "Hosen",
  "Kleider",
  "Schuhe",
  "Accessoires",
];

export default function WardrobePage() {
  const [items, setItems] = useState<ClothingItemResponse[]>([]);
  const [activeCategory, setActiveCategory] = useState("Alle");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listItems()
      .then(setItems)
      .catch((err: unknown) => {
        const message =
          err instanceof Error ? err.message : "Unbekannter Fehler";
        setError(message);
      })
      .finally(() => setLoading(false));
  }, []);

  const filteredItems =
    activeCategory === "Alle"
      ? items
      : items.filter((item) => item.category === activeCategory);

  return (
    <div className="wardrobe-page">
      <div className="wardrobe-page__header">
        <h1 className="wardrobe-page__title">Meine Garderobe</h1>
      </div>

      <CategoryFilter
        categories={ALL_CATEGORIES}
        activeCategory={activeCategory}
        onSelect={setActiveCategory}
      />

      {error && !loading ? (
        <div className="wardrobe-page__empty">
          <div className="wardrobe-page__empty-icon">&#9733;</div>
          <h2 className="wardrobe-page__empty-title">
            Deine Garderobe wartet auf dich!
          </h2>
          <p className="wardrobe-page__empty-text">
            Sobald die Backend-Endpunkte bereit sind, erscheint hier deine
            glamour&ouml;se Garderobe.
          </p>
        </div>
      ) : (
        <WardrobeGrid items={filteredItems} loading={loading} />
      )}
    </div>
  );
}
