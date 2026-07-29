VERDICT: BUGS_FOUND

Der Testlauf zeigt zwei klar beobachtbare Produktfehler, die die Auslieferung unbrauchbar machen.

- **Titel:** CSP-Header wird nicht gesendet
  **Symptom:** Die Anwendung liefert keinen `Content-Security-Policy`-Header in HTTP-Antworten aus. Verletzt AC-16.
  **Repro:** E2E-Test `security.spec.cjs` registriert alle response-Header und prüft, ob ein CSP-Header vorhanden ist. Der Test bricht mit `expect(cspFound).toBe(true)` ab, weil `cspFound` den Wert `false` behält.
  **Evidence:** > `expect(cspFound).toBe(true);` — `Expected: true`, `Received: false` (Testbericht, `security.spec.cjs:41`)
  **Suspected file(s):** `backend/main.py` (CSPMiddleware wird möglicherweise nicht auf alle Antworten angewendet, z. B. auf statische Dateien oder die Startseite)
  **Severity:** high

- **Titel:** Ausgeliefertes Frontend kann das Backend nicht erreichen – gesamte Benutzerinteraktion blockiert
  **Symptom:** Nach dem Absenden des Login-Formulars bleibt der Benutzer auf der Login-Seite; es erfolgt keine Weiterleitung zur Garderobe. Sämtliche E2E-Tests, die eine Anmeldung voraussetzen (Authentifizierung, Outfits, Kleiderschrank), scheitern mit Timeout bei `page.waitForURL('**/wardrobe')` oder beim Warten auf Buttons, weil die API-Aufrufe nie beantwortet werden. Das Produkt ist im ausgelieferten Zustand nicht bedienbar.
  **Repro:** Produktions-Build (`dist`) ausliefern und versuchen, sich über das Formular einzuloggen. Die Vite-Entwicklungsproxys laufen nicht; `VITE_API_URL` ist nicht auf den Backend-Port (8000) gesetzt. Die API-Anfragen gehen an den Ursprung des Frontend-Servers (Port 5173) und schlagen fehl.
  **Evidence:** Mehrere Timeout-Fehler in den E2E-Tests, z. B.:  
  > `page.waitForURL: Test timeout of 12000ms exceeded.`  
  > (auth.spec.cjs:19, outfits.spec.cjs:19, wardrobe.spec.cjs:21, jeweils nach `page.click('button[type="submit"]')`)
  **Suspected file(s):** `frontend/src/api/client.ts` (`API_BASE` nutzt `VITE_API_URL` oder leeren String), `frontend/vite.config.ts` (Proxy-Einstellungen nur für `serve`-Modus), fehlende Umgebungsvariable `VITE_API_URL` im Produktions-Build
  **Severity:** critical