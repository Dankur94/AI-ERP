# Phase 6 — Benutzeroberflaeche (2-3 Wochen)

**Woche:** 11-13
**Status:** Offen

## Was

Dashboard, Upload-Flows, Listen, Export-Funktionen.

## Warum

Ohne UI kann kein Kunde das Produkt nutzen.

## Output / Deliverables

Klickbare, benutzerfreundliche Oberflaeche fuer die Zielpersonas.

## Kern-Screens

1. **Dashboard** — Ueberblick: offene Deklarationen, Status, Fristen
2. **Lieferungen-Liste** — Alle Importe mit Filtermoglichkeiten
3. **Lieferung-Detail** — Einzelansicht mit CBAM-Daten, LLM-Extraktionen, Korrekturen
4. **Dokumenten-Upload** — Drag & Drop, Fortschrittsanzeige, LLM-Verarbeitung
5. **CBAM-Deklaration** — Quartalsbericht erstellen, pruefen, exportieren
6. **Lieferanten-Verwaltung** — Lieferanten pflegen, Verifizierungsstatus
7. **Einstellungen** — Unternehmensdaten, Nutzer, Rollen

## Design-Prinzipien

- Mobile-first (aber Desktop ist primaer)
- Progressive Disclosure — Komplexitaet nur wenn noetig
- Inline-Hilfe und Tooltips fuer Compliance-Begriffe
- Barrierefreiheit (WCAG 2.1 AA)

## Checkliste

- [ ] Dashboard implementiert
- [ ] Lieferungen-CRUD funktioniert
- [ ] Dokumenten-Upload mit LLM-Feedback
- [ ] CBAM-Deklaration erstellen und exportieren
- [ ] Lieferanten-Verwaltung
- [ ] Responsive Design getestet
- [ ] Usability-Test mit mind. 2 Personen
