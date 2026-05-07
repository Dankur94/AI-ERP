# Sicherheit — Einordnung Bank vs. Wir

Was Banken machen, was wir davon brauchen, und was spaeter kommt.

---

## Verschluesselung (Ende-zu-Ende + HSM)

| | Bank | Wir (Stufe 1) |
|---|---|---|
| **HSM** | Physisches Geraet (5.000-20.000 USD) oder Cloud (1.500 USD/Monat) | Nicht noetig |
| **Ende-zu-Ende** | Pflicht auf jedem Layer | HTTPS (Transport) + bcrypt (Passwoerter) + DB nicht oeffentlich |
| **Aufwand** | Hoch, teuer | Bereits abgedeckt durch Standard-Setup |

---

## Zwei-Faktor-Authentifizierung (2FA)

| Aspekt | Detail |
|---|---|
| **Aufwand** | Niedrig — fertige Library (`pyotp`), ein Nachmittag |
| **Wie es funktioniert** | Nutzer scannt QR-Code mit Google Authenticator, gibt 6-stelligen Code beim Login ein |
| **Wann** | Stufe 2 — wenig Aufwand, viel Sicherheitsgewinn |
| **Stufe 1** | Noch nicht noetig, normaler Login reicht |

---

## Echtzeit-Ueberwachung / Security Operations Center

### Was eine Bank hat
Ein ganzes Team das 24/7 auf Bildschirme schaut: Wer loggt sich ein, von wo, wie oft, gibt es Muster.

### Kann Claude das uebernehmen?
Nicht als 24/7-Waechter. Claude antwortet wenn man fragt — laeuft nicht dauerhaft. Jede Minute Logs an Claude schicken waere zu teuer und zu langsam.

### Was stattdessen funktioniert

| Stufe | Loesung | Aufwand |
|---|---|---|
| **Stufe 1** | Sentry (automatische Fehler-Alerts, kostenlos bis 5k Events) + einfache Regeln ("5 fehlgeschlagene Logins → Email an dich") | Gering |
| **Stufe 2** | Strukturierte Logs → einmal taeglich durch Claude zusammenfassen ("Fasse die Auffaelligkeiten der letzten 24h zusammen") | Mittel |
| **Stufe 3+** | Echtes Monitoring-Tool (Grafana, Datadog) | Hoch |

### Entscheidung

Claude nicht als Waechter, sondern als **taeglicher Analyst** — Logs von gestern pruefen, Auffaelliges melden. Machbar, guenstig, nuetzlich.

---

## Zusammenfassung

| Massnahme | Bank | Wir Stufe 1 | Wir spaeter |
|---|---|---|---|
| HSM | Pflicht | Nein | Nein (nie noetig fuer KMU-Tool) |
| Ende-zu-Ende | Ueberall | HTTPS + bcrypt reicht | — |
| 2FA | Immer | Nein | Stufe 2 (pyotp, ein Nachmittag) |
| 24/7 SOC Team | Ja, Millionen/Jahr | Nein | Claude als taeglicher Log-Analyst (Stufe 2) |
| Monitoring | Datadog/Splunk | Sentry (kostenlos) | Grafana (Stufe 3) |
