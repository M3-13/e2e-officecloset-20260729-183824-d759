import type { ClothingItemResponse } from "../api/client";
import "./OutfitPreview.css";

const API_BASE = import.meta.env.VITE_API_URL || "";

interface OutfitPreviewProps {
  items: ClothingItemResponse[];
  onRemove?: (category: string) => void;
}

export default function OutfitPreview({ items, onRemove }: OutfitPreviewProps) {
  return (
    <div className="outfit-preview">
      {items.length === 0 ? (
        <div className="outfit-preview__empty">
          <span className="outfit-preview__empty-icon">&#9733;</span>
          <p>Wählen Sie Kleidungsstücke aus,<br />um Ihr Outfit zu gestalten.</p>
        </div>
      ) : (
        items.map((item) => (
          <div key={item.id} className="outfit-preview__slot">
            <div className="outfit-preview__image-wrap">
              <img
                src={`${API_BASE}/static/${item.image_path}`}
                alt={item.name}
                className="outfit-preview__image"
              />
            </div>
            <div className="outfit-preview__info">
              <span className="outfit-preview__name">{item.name}</span>
              <span className="outfit-preview__category">{item.category}</span>
            </div>
            {onRemove && (
              <button
                type="button"
                className="outfit-preview__remove"
                onClick={() => onRemove(item.category)}
                aria-label={`${item.name} entfernen`}
              >
                &#10005;
              </button>
            )}
          </div>
        ))
      )}
    </div>
  );
}
