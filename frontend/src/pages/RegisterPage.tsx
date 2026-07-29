import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [passwordRepeat, setPasswordRepeat] = useState("");
  const [privacyAccepted, setPrivacyAccepted] = useState(false);
  const [error, setError] = useState("");
  const [fieldError, setFieldError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  function validate(): boolean {
    if (password.length < 8) {
      setFieldError("Passwort muss mindestens 8 Zeichen lang sein");
      return false;
    }
    if (password !== passwordRepeat) {
      setFieldError("Passwörter stimmen nicht überein");
      return false;
    }
    if (!privacyAccepted) {
      setFieldError("Bitte akzeptieren Sie die Datenschutzerklärung");
      return false;
    }
    setFieldError("");
    return true;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    if (!validate()) return;
    setSubmitting(true);
    try {
      await register(email, password, privacyAccepted);
      navigate("/wardrobe", { replace: true });
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : "Registrierung fehlgeschlagen";
      setError(msg);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1 className="auth-title">Registrierung</h1>
        <form onSubmit={handleSubmit}>
          {error && <div className="form-alert">{error}</div>}
          {fieldError && <div className="form-alert">{fieldError}</div>}
          <div className="form-group">
            <label className="form-label" htmlFor="register-email">
              E-Mail
            </label>
            <input
              id="register-email"
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
            <label className="form-label" htmlFor="register-password">
              Passwort
            </label>
            <input
              id="register-password"
              className="form-input"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Mindestens 8 Zeichen"
              required
              minLength={8}
              autoComplete="new-password"
            />
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="register-password-repeat">
              Passwort wiederholen
            </label>
            <input
              id="register-password-repeat"
              className="form-input"
              type="password"
              value={passwordRepeat}
              onChange={(e) => setPasswordRepeat(e.target.value)}
              placeholder="Passwort wiederholen"
              required
              autoComplete="new-password"
            />
          </div>
          <div className="form-checkbox-group">
            <input
              id="register-privacy"
              className="form-checkbox"
              type="checkbox"
              checked={privacyAccepted}
              onChange={(e) => setPrivacyAccepted(e.target.checked)}
            />
            <label className="form-checkbox-label" htmlFor="register-privacy">
              Ich akzeptiere die{" "}
              <a href="#" onClick={(e) => e.preventDefault()}>
                Datenschutzerklärung
              </a>
            </label>
          </div>
          <button
            type="submit"
            className="btn-primary"
            disabled={submitting}
          >
            {submitting ? "Konto wird erstellt..." : "Registrieren"}
          </button>
        </form>
        <div className="auth-link">
          Bereits registriert?{" "}
          <Link to="/login">Jetzt anmelden</Link>
        </div>
      </div>
    </div>
  );
}
