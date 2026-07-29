VERDICT: BUGS_FOUND

- **Titel**: Authentifizierung (Registrierung/Login) schlägt mit HTTP 500 fehl – JWT_SECRET nicht konfiguriert
- **Symptom**: Benutzer können sich weder über die Benutzeroberfläche noch per API-Aufruf anmelden, weil der Server einen internen Fehler (500) zurückgibt. Die E2E‑Tests (auth, outfits, wardrobe) brechen alle beim Versuch, sich zu registrieren/anzumelden, mit Timeout ab – die erwartete Weiterleitung nach `/wardrobe` erfolgt nie. Die geschützten Bereiche der Anwendung sind dadurch für niemanden erreichbar.
- **Repro**: Backend starten und ohne vorheriges Setzen von `JWT_SECRET` eine Registrierung (`POST /api/auth/register`) oder Anmeldung (`POST /api/auth/login`) durchführen; der Server antwortet mit 500. Im Browser `http://localhost:5173/register` oder `/login` ausfüllen und absenden; die UI bleibt hängen oder zeigt eine Fehlermeldung, es erfolgt keine Weiterleitung.
- **Evidence**:  
  - `backend/auth.py` wirft bei leerem `JWT_SECRET` `HTTPException(status_code=500, detail="JWT_SECRET not configured")`.  
  - In dem Playwright‑Test‑Log erscheint mehrfach `Test timeout of 12000ms exceeded` beim `page.waitForURL('**/wardrobe')`, z.B.:  
    `Error: page.waitForURL: Test timeout of 12000ms exceeded.` (Zeile 19 in `e2e/outfits.spec.cjs`).  
  - API‑Smoke‑Test auf `/api/health` erfolgreich (200), was zeigt, dass der Server grundsätzlich läuft, aber die authentifizierungsrelevanten Endpunkte nicht funktionieren.
- **Suspected file(s)**: `backend/auth.py` (Zeile `if not secret: …`), `backend/config.py` (kein Fallback-Wert für `JWT_SECRET`), ggf. fehlende Setzung der Umgebungsvariable im Start‑Rezept `RUN.json`.
- **Severity**: critical

- **Titel**: Content‑Security‑Policy‑Header wird auf den ausgelieferten Seiten nicht gesetzt
- **Symptom**: AC‑16 (CSP setzen) ist nicht erfüllt; der Test `AC-08: CSP header is set on responses` scheitert, weil der Browser keinen `Content-Security-Policy`‑Header im Response der Hauptseite findet.
- **Repro**: Die Root‑Route (`/`) abrufen und den HTTP‑Response‑Header `Content-Security-Policy` prüfen – er fehlt.
- **Evidence**:  
  ```
  9) e2e\security.spec.cjs:29:3 › Security / XSS › AC-08: CSP header is set on responses
      Error: expect(received).toBe(expected) // Object.is equality
      Expected: true
      Received: false
        at …\security.spec.cjs:41:22
  ```
- **Suspected file(s)**: `backend/main.py` (Klasse `CSPMiddleware` und/oder deren Anmeldung in der Middleware‑Pipeline), möglicherweise auch die Art der statischen Dateiauslieferung, die den Header nicht durchreicht.
- **Severity**: high

- **Titel**: Fehlende Funktionalität aus nicht integriertem Merge‑Request MR !23
- **Symptom**: Laut Testbericht wurde der geplante Merge‑Request !23 nicht gemergt ("left open, never merged"). Die in diesem Ticket enthaltenen Features/Anpassungen sind daher nicht im Produkt vorhanden, was eine Lücke gegenüber der ursprünglichen Spezifikation darstellt. Da der genaue Inhalt von MR !23 nicht im Bericht steht, kann die fehlende Fähigkeit nicht näher benannt werden, sie ist jedoch als zugesicherte, nicht gelieferte Funktionalität zu werten.
- **Repro**: Nicht anwendbar, da das Ticket nicht im Produkt enthalten ist.
- **Evidence**:  
  Abschnitt "PROMISED BUT NOT DELIVERED" im Testbericht: "MR !23 — left open, never merged; its changes are NOT in the product".
- **Suspected file(s)**: Alle Dateien, die MR !23 betroffen hätte – der Merge ist nicht erfolgt, daher keine Änderungen im Branch.
- **Severity**: high