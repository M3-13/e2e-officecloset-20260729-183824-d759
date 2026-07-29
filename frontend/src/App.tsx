import { Routes, Route, Navigate, Link, Outlet } from "react-router-dom";
import { useAuth } from "./contexts/AuthContext";
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import WardrobePage from "./pages/WardrobePage";
import OutfitCreatorPage from "./pages/OutfitCreatorPage";
import OutfitsListPage from "./pages/OutfitsListPage";
import "./App.css";

function ProtectedRoute() {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return null;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}

function Navbar() {
  const { isAuthenticated, logout, deleteAccount } = useAuth();

  async function handleDeleteAccount() {
    if (!window.confirm("Möchten Sie Ihr Konto wirklich löschen? Alle Ihre Kleidungsstücke, Outfits und Bilder werden unwiderruflich entfernt.")) {
      return;
    }
    try {
      await deleteAccount();
    } catch {
      alert("Fehler beim Löschen des Kontos.");
    }
  }

  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <Link to="/" className="navbar-brand">
          Hollywood Closet
        </Link>
        <div className="navbar-links">
          <Link to="/" className="navbar-link">
            Home
          </Link>
          <Link to="/wardrobe" className="navbar-link">
            Garderobe
          </Link>
          <Link to="/outfits" className="navbar-link">
            Outfits
          </Link>
          {isAuthenticated ? (
            <>
              <button
                type="button"
                className="navbar-link navbar-btn navbar-btn-danger"
                onClick={handleDeleteAccount}
              >
                Konto löschen
              </button>
              <button
                type="button"
                className="navbar-link navbar-btn"
                onClick={logout}
              >
                Abmelden
              </button>
            </>
          ) : (
            <Link to="/login" className="navbar-link">
              Anmelden
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
}

function Layout() {
  return (
    <>
      <Navbar />
      <main className="main-content">
        <Outlet />
      </main>
    </>
  );
}

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route element={<ProtectedRoute />}>
          <Route path="/wardrobe" element={<WardrobePage />} />
          <Route path="/outfits" element={<OutfitsListPage />} />
          <Route path="/outfits/create" element={<OutfitCreatorPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
