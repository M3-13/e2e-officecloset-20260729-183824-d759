import { useState } from "react";
import type { ClothingItemResponse } from "../api/client";
import "./WardrobeGrid.css";

interface WardrobeGridProps {
  items: ClothingItemResponse[];
  loading: boolean;
}

function getImageUrl(imagePath: string): string {
  if (imagePath.startsWith("http")) return imagePath;
  const base = import.meta.env.VITE_API_URL || "";
  const normalizedPath = imagePath.startsWith("/") ? imagePath : `/${imagePath}`;
  return `${base}${normalizedPath}`;
}

function WardrobeCard({ item }: { item: ClothingItemResponse }) {
  const [imageFailed, setImageFailed] = useState(false);

  return (
    <div className="wardrobe-card">
      <div className="wardrobe-card__image-wrapper">
        {!imageFailed ? (
          <img
            src={getImageUrl(item.image_path)}
            alt={item.name}
            className="wardrobe-card__image"
            loading="lazy"
            onError={() => setImageFailed(true)}
          />
        ) : (
          <div className="wardrobe-card__image-fallback">
            <span className="wardrobe-card__image-fallback-icon">&#9830;</span>
          </div>
        )}
        <div className="wardrobe-card__glow" />
      </div>
      <div className="wardrobe-card__body">
        <span className="wardrobe-card__badge">{item.category}</span>
        <h3 className="wardrobe-card__name">{item.name}</h3>
      </div>
    </div>
  );
}

export default function WardrobeGrid({ items, loading }: WardrobeGridProps) {
  if (loading) {
    return (
      <div className="wardrobe-grid">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="wardrobe-card wardrobe-card--skeleton">
            <div className="wardrobe-card__image-wrapper wardrobe-card__image-wrapper--skeleton" />
            <div className="wardrobe-card__body">
              <div className="wardrobe-card__skeleton-badge" />
              <div className="wardrobe-card__skeleton-name" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="wardrobe-grid__empty">
        <div className="wardrobe-grid__empty-icon">&#9733;</div>
        <h2 className="wardrobe-grid__empty-title">
          Deine Garderobe wartet auf dich!
        </h2>
        <p className="wardrobe-grid__empty-text">
          Lade dein erstes Kleidungsst&uuml;ck hoch und bringe Glamour in
          deinen Kleiderschrank.
        </p>
        <button type="button" className="wardrobe-grid__empty-cta">
          Erstes Teil hochladen
        </button>
      </div>
    );
  }

  return (
    <div className="wardrobe-grid">
      {items.map((item) => (
        <WardrobeCard key={item.id} item={item} />
      ))}
    </div>
  );
}
