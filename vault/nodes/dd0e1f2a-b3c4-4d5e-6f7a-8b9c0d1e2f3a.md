# Phase 8 — Production-Readiness (1-2 Wochen)

**Woche:** 16-17
**Status:** Offen

## Was

Backups, Sicherheit, DSGVO, Rechtstexte, Monitoring, Notfallplan.

## Warum

Bevor der erste echte Kunde live geht, muss das wasserdicht sein.

## Output / Deliverables

Checkliste komplett abgehakt, Go-Live-faehig.

## Bereiche

### Sicherheit
- Penetration-Test (mind. automatisiert)
- OWASP Top 10 geprueft
- Rate Limiting, CORS, CSP Headers
- Secrets Management (keine Secrets im Code)

### DSGVO / Datenschutz
- Datenschutzerklaerung
- Auftragsverarbeitungsvertrag (AVV) Template
- Daten-Loeschkonzept
- Cookie-Banner (falls Web)

### Betrieb
- Automatische Backups (DB + Dateien)
- Backup-Restore getestet
- Monitoring & Alerting konfiguriert
- Runbook fuer haeufige Probleme
- Notfallplan (Was wenn DB down? Was wenn API-Limit?)

### Rechtliches
- AGB / Nutzungsbedingungen
- Impressum
- Haftungsausschluss fuer LLM-Ergebnisse

## Checkliste

- [ ] Security-Scan durchgefuehrt
- [ ] OWASP Top 10 geprueft
- [ ] DSGVO-Dokumente erstellt
- [ ] Backups laufen automatisch
- [ ] Backup-Restore getestet
- [ ] Monitoring & Alerting aktiv
- [ ] Runbook geschrieben
- [ ] Rechtstexte vorhanden
- [ ] Staging → Production Migration getestet
- [ ] Go-Live Freigabe erteilt
