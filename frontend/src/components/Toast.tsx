import { useEffect, type ReactNode } from "react";
import "./Toast.css";

interface ToastProps {
  children: ReactNode;
  variant?: "success" | "error" | "info";
  onClose: () => void;
  durationMs?: number;
}

export default function Toast({
  children,
  variant = "info",
  onClose,
  durationMs = 3500,
}: ToastProps) {
  useEffect(() => {
    const timer = setTimeout(onClose, durationMs);
    return () => clearTimeout(timer);
  }, [onClose, durationMs]);

  return (
    <div className={`toast toast--${variant}`} role="alert">
      <span className="toast__message">{children}</span>
      <button
        type="button"
        className="toast__close"
        onClick={onClose}
        aria-label="Schließen"
      >
        ✕
      </button>
    </div>
  );
}
