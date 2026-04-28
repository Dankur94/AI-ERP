# Changelog

Alle Aenderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/) und [Semantic Versioning](https://semver.org/).

<!-- TEMPLATE fuer neue Eintraege (oben einfuegen):
## [vX.Y.Z] - YYYY-MM-DD
### Hinzugefuegt
### Geaendert
### Behoben
### Entfernt
-->

## [Unreleased]

### Hinzugefuegt
- **L3: Kundenisolation (tenant_id)**
  - tenant_id Spalte in invoices-Tabelle (Default: "default" fuer Stufe 1)
  - Alle DB-Queries filtern nach tenant_id
  - Automatische Migration fuer bestehende Datenbanken
  - API-Endpoints erzwingen tenant_id bei allen Operationen
- **Modul 1: Claude Vision API Integration**
  - Extraction-Service mit echtem Claude Vision API Support (L5: Adapter Pattern)
  - Automatischer Fallback auf Mock wenn kein API Key konfiguriert
  - JSON-Parsing mit Code-Fence-Handling
  - Config-Loader: config.yaml (YAML) oder Umgebungsvariablen (L12: Human-Readable)
  - anthropic + pyyaml als neue Dependencies
- **Modul 2: Suche & Filter (Backend)**
  - GET /api/invoices/search — Volltextsuche ueber Lieferant, Rechnungsnummer, Dateiname
  - Filter: Status, Lieferant, Datumsbereich, Waehrung
  - Kombinierbare Filter + Freitextsuche
  - Tenant-isolierte Ergebnisse (L3)
- **Modul 2: Suche & Filter (Frontend)**
  - SearchView mit Suchleiste und Live-Suche (Debounce 300ms)
  - Filter-Dropdowns: Status, Lieferant, Datum von/bis, Waehrung
  - Ergebnistabelle mit Klick-Navigation zur Rechnungsdetailansicht
  - Navigation: "Search" Link im Header neben "Upload"
  - Route: /search
- **Modul 3: Matching / Abgleich (Backend)**
  - POST /api/matches — Zwei Rechnungen vergleichen
  - Automatischer Feldvergleich (Lieferant, Betrag, Waehrung, Datum, Positionen)
  - Positionen-Matching (exakt + partiell)
  - Abweichungserkennung: match, mismatch, missing_a, missing_b
  - GET /api/matches — Liste aller Vergleiche
  - GET /api/matches/{id} — Vergleichsdetails
  - DELETE /api/matches/{id} — Vergleich loeschen
  - Tenant-isoliert (L3)
- **Modul 3: Matching / Abgleich (Frontend)**
  - MatchView: Zwei Rechnungen per Dropdown auswaehlen
  - Vergleichsergebnis mit farbiger Markierung (gruen=match, rot=mismatch, gelb=missing)
  - Gesamtdifferenz hervorgehoben
  - Match-Verlauf mit Loeschfunktion
  - Route: /matches, Navigation: "Match" im Header
- **Modul 4: Reports (Backend)**
  - GET /api/reports/summary — Zusammenfassung (Anzahl, Summen, nach Status/Lieferant/Waehrung)
  - GET /api/reports/export/csv — CSV-Export aller Rechnungen
  - Datumsfilter fuer Summary und Export
  - Tenant-isoliert (L3)
  - L4: CSV fuer Stufe 1, PDF/Excel spaeter
- **Modul 4: Reports (Frontend)**
  - ReportView: 4 KPI-Karten (Anzahl, Summe, Lieferanten, Waehrungen)
  - Aufschluesselung nach Status, Waehrung, Lieferant
  - CSV-Download-Button
  - Datumsfilter
  - Route: /reports, Navigation: "Reports" im Header
- **Modul 5: Alerts — Ueberfaellige Zahlungen**
  - GET /api/alerts — berechnet ueberfaellige Rechnungen (payment_due < heute, status != confirmed)
  - Kein neues Datenmodell — berechnet aus bestehenden Daten (L4)
  - In-App Badge im Header mit Anzahl (pollt alle 60s)
  - AlertView: Tabelle mit Lieferant, Betrag, Faelligkeitsdatum, "Days Overdue"
  - Farbige Badges (gelb < 14 Tage, rot > 14 Tage ueberfaellig)
  - Klick auf Zeile navigiert zur Rechnungsdetailansicht
  - Tenant-isoliert (L3)
  - Route: /alerts, Navigation: "Alerts" im Header
  - Weitere Alert-Typen auf Kundennachfrage (L4)
- **Tests (65 Tests)**
  - test_database.py: CRUD, Tenant-Isolation (L3), Suche & Filter (Modul 2)
  - test_api.py: Alle Endpoints inkl. Upload, Search, PDF-Serving
  - test_extraction.py: Mock-Extraktion, Claude-Response-Parsing
  - test_matching.py: Vergleichslogik, API-Endpoints, Tenant-Isolation
  - test_reports.py: Summary-Statistiken, CSV-Export, Datumsfilter
  - test_alerts.py: Overdue-Erkennung, Tenant-Isolation, Sortierung, API
  - conftest.py: Isolierte Test-DB pro Test, temporaere Upload-Dirs
- **Modul 6: UX-Grundlagen (Recherche)**
  - Vault-Node mit Recherche-Punkten: Auge (F/Z-Pattern, Fovea, Pre-attentive Processing, Gestaltgesetze), Gehirn (Cognitive Load, Progressive Disclosure, Hick's Law), Hand (Fitts's Law, Touch-Targets)
  - Dashboard-Empfehlungen abgeleitet
  - Leseliste und Persona-spezifische Widgets dokumentiert
- config.example.yaml erweitert (Anthropic API Key, Model, DB-Pfad)

### Vorhanden (aus vorheriger Arbeit)
- **Modul 1: Dokumenten-Erfassung (Backend)**
  - FastAPI Backend mit Upload-Endpunkt (POST /api/invoices/upload)
  - SQLite Datenbank (invoices + line_items Tabellen, inkl. Confidence-Scores)
  - Mock-Extraktion (realistischer Shanghai Electronics Dummy-Daten)
  - CRUD-Endpoints: GET/PUT invoices, PDF-Download
  - Health-Check Endpoint (/api/health)
- **Modul 1: Dokumenten-Erfassung (Frontend)**
  - Vue.js 3 Frontend mit Vite
  - Drag & Drop Upload-Zone (Multi-PDF, nur PDF-Filter)
  - Split-View: PDF links (iframe), extrahierte Daten rechts
  - Editierbares Korrektur-Formular mit Confidence-Badges (Sicher/Pruefen/Unsicher)
  - Positionen-Tabelle (editierbar)
  - Rechnungsliste mit Status-Anzeige
  - Speichern + Bestaetigen Buttons
- Start-Scripts (start-backend.sh, start-frontend.sh)
- Python venv Konfiguration
- Master-MD (Claude Briefing) unter Software-Zweig
- CLAUDE.md aktualisiert mit Produkt, Leitprinzip, Lessons, Struktur
- CLAUDE.local.md fuer lokale Einstellungen
- Ordnerstruktur: src/api/, src/web/, src/shared/, docs/sessions/, docs/domain/
- 5 Personas (David, Michelle, Raymond, Jenny, Dr. Kevin)
- 16 Architektur-Lessons (L1-L16) mit Ranking nach Leitprinzip
- 4 Schutzschichten gegen Qualitaetsverlust
- 6 Software-Module definiert (Erfassung → Dashboard)
- Wettbewerbsanalyse (Tofu, SAP Concur, Xero, Yonyou)

### Geaendert
- Frontend UI-Sprache von Deutsch auf Englisch (Kunden in Hong Kong)
- Header-Text: "Invoice Capture" → "Invoice Pipeline" (spiegelt 4 Module wider)
- Navigation: 5 Links (Upload, Search, Match, Reports, Alerts) mit Alert-Badge

### Behoben
- PDF-Preview: Content-Disposition von "attachment" auf "inline" (PDF wurde heruntergeladen statt angezeigt)
- Upload: Content-Type Check gelockert (manche Browser senden anderen MIME-Type fuer PDFs)
- Datenbank: Confidence-Spalten fehlten im initialen Schema

---

## [v1.0.0] - 2026-04-22

### Hinzugefuegt
- Projektstruktur erstellt (src/, docs/, tests/, modules/)
- CLAUDE.md mit Projektkontext
- config.example.yaml (Config-Template)
- deploy.sh (Git-based Deploy)
- .gitignore konfiguriert (config.yaml excluded)
- Modul-Entwicklungsanleitung (docs/adding-modules.md)
- Git-Repository initialisiert
