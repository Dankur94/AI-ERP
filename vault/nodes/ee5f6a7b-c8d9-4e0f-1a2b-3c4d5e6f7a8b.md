# Phase 3 — Fundament bauen (2 Wochen)

**Woche:** 5-6
**Status:** Offen

## Was

Auth, Datenbank, Multi-Tenancy, Audit-Trail, Observability aufsetzen.

## Warum

Das unsichtbare Fundament, das nachtraeglich einzuziehen zehnmal teurer waere.

## Output / Deliverables

Lauffaehige App-Grundstruktur mit Login, aber noch ohne Business-Features.

## Komponenten

1. **Authentication & Authorization** — Login, Rollen, Permissions
2. **Datenbank-Schema** — Migrations, Seed-Daten, Multi-Tenancy
3. **Multi-Tenancy** — Mandantentrennung (Row-Level, Schema-Level, oder DB-Level)
4. **Audit-Trail** — Wer hat wann was geaendert (Compliance-kritisch!)
5. **Observability** — Logging, Metrics, Tracing
6. **Health-Checks** — Readiness/Liveness fuer Deployment
7. **Error Handling** — Zentrale Fehlerbehandlung, Error-Codes

## Checkliste

- [ ] Auth-System laeuft (Login/Logout/Register)
- [ ] Rollen & Permissions implementiert
- [ ] Datenbank-Migrations funktionieren
- [ ] Multi-Tenancy eingebaut
- [ ] Audit-Trail loggt alle Aenderungen
- [ ] Logging & Monitoring aktiv
- [ ] Health-Check-Endpunkt vorhanden
- [ ] Erster Deploy auf Staging erfolgreich
