import { useState, type FormEvent } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [passwordRepeat, setPasswordRepeat] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");

    if (password !== passwordRepeat) {
      setError("Passwörter stimmen nicht überein");
      return;
    }
    if (password.length < 8) {
      setError("Passwort muss mindestens 8 Zeichen lang sein");
      return;
    }

    setSubmitting(true);
    try {
      await register(email, password);
      navigate("/wardrobe", { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1 className="auth-heading">Registrierung</h1>
        <form onSubmit={handleSubmit} className="auth-form">
          <label className="auth-label">
            E-Mail
            <input
              type="email"
              className="auth-input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
            />
          </label>
          <label className="auth-label">
            Passwort
            <input
              type="password"
              className="auth-input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="new-password"
              minLength={8}
            />
          </label>
          <label className="auth-label">
            Passwort wiederholen
            <input
              type="password"
              className="auth-input"
              value={passwordRepeat}
              onChange={(e) => setPasswordRepeat(e.target.value)}
              required
              autoComplete="new-password"
              minLength={8}
            />
          </label>
          {error && <div className="auth-error">{error}</div>}
          <button type="submit" className="auth-btn" disabled={submitting}>
            {submitting ? "Wird registriert..." : "Registrieren"}
          </button>
        </form>
        <p className="auth-switch">
          Bereits registriert? <Link to="/login">Jetzt anmelden</Link>
        </p>
      </div>
    </div>
  );
}
