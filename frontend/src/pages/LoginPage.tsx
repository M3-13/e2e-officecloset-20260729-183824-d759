import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await login(email, password);
      navigate("/wardrobe", { replace: true });
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : "Anmeldung fehlgeschlagen";
      setError(msg);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1 className="auth-title">Anmeldung</h1>
        <form onSubmit={handleSubmit}>
          {error && <div className="form-alert">{error}</div>}
          <div className="form-group">
            <label className="form-label" htmlFor="login-email">
              E-Mail
            </label>
            <input
              id="login-email"
              className="form-input"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="ihre@email.de"
              required
              autoComplete="email"
            />
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="login-password">
              Passwort
            </label>
            <input
              id="login-password"
              className="form-input"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Ihr Passwort"
              required
              autoComplete="current-password"
            />
          </div>
          <button
            type="submit"
            className="btn-primary"
            disabled={submitting}
          >
            {submitting ? "Wird angemeldet..." : "Anmelden"}
          </button>
        </form>
        <div className="auth-link">
          Noch kein Konto?{" "}
          <Link to="/register">Jetzt registrieren</Link>
        </div>
      </div>
    </div>
  );
}
