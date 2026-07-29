import { Link } from "react-router-dom";
import "./HomePage.css";

export default function HomePage() {
  return (
    <div className="home-page">
      <section className="hero">
        <div className="hero-content">
          <div className="hero-badge">Willkommen in Ihrem</div>
          <h1 className="hero-title">Hollywood Closet</h1>
          <p className="hero-subtitle">
            Ihr glamour&ouml;ser Kleiderschrank-Manager. Organisieren Sie Ihre Garderobe mit
            Stil, kreieren Sie atemberaubende Outfits und treten Sie jeden Tag wie ein Star auf
            den roten Teppich.
          </p>
          <div className="hero-actions">
            <Link to="/register" className="btn btn-primary">
              Jetzt loslegen
            </Link>
            <Link to="/login" className="btn btn-secondary">
              Anmelden
            </Link>
          </div>
        </div>
        <div className="hero-visual">
          <div className="hero-sparkle sparkle-1" />
          <div className="hero-sparkle sparkle-2" />
          <div className="hero-sparkle sparkle-3" />
          <div className="hero-mirror">
            <div className="hero-mirror-inner" />
          </div>
        </div>
      </section>

      <section className="features">
        <h2 className="features-title">Ihre Vorteile</h2>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">&#10032;</div>
            <h3>Digitale Garderobe</h3>
            <p>
              Fotografieren Sie Ihre Kleidungsst&uuml;cke und durchst&ouml;bern Sie Ihre
              gesamte Garderobe in einer eleganten Galerie &ndash; immer griffbereit.
            </p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">&#9830;</div>
            <h3>Outfit Creator</h3>
            <p>
              Kombinieren Sie Oberteile, Hosen, Kleider, Schuhe und Accessoires zu perfekten
              Outfits und speichern Sie Ihre Kreationen.
            </p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">&#9818;</div>
            <h3>Red-Carpet-Stil</h3>
            <p>
              Eine glamour&ouml;se, luxuri&ouml;se Oberfl&auml;che, die Ihr
              Stilempfinden widerspiegelt &ndash; mit goldenen Akzenten und weichen Animationen.
            </p>
          </div>
        </div>
      </section>

      <footer className="home-footer">
        <p>Hollywood Closet &mdash; Because every day is a red carpet.</p>
      </footer>
    </div>
  );
}
