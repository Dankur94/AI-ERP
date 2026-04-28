# Phase 2 — Architektur-Entscheidungen

**Status:** Offen

## Leitprinzip

Architektur muss zum Stufenplan passen: Heute fuer 5-15 Leute bauen, aber so, dass es bis Enterprise skaliert.

```
Stufe 1 (jetzt)       Stufe 2 (12M)        Stufe 3 (24M)        Stufe 4 (48M)
Custom pro Kunde  →   Wiederverwendbare  →  SaaS-Produkt     →   Enterprise
                      Module
```

## 5 Entscheidungen die jetzt fallen muessen

| # | Entscheidung | Warum jetzt |
|---|---|---|
| 1 | **Modular** — Jede Loesung als trennbares Modul | Stufe 2 braucht wiederverwendbare Bausteine |
| 2 | **Multi-Tenant** — Kundendaten von Tag 1 getrennt | Spaeter umbauen ist extrem teuer |
| 3 | **API-first** — Alles ueber APIs, kein monolithisches UI | WhatsApp, Excel-Import, Drittsysteme muessen andocken |
| 4 | **Dokument-zentrisch** — PDF/Foto rein → strukturierte Daten raus | Das ist der Kern-Workflow aller 3 Personas |
| 5 | **LLM als Service-Layer** — Claude fuer Extraktion, nicht als UI | LLM-Anbieter wechselbar halten |

## Module die aus Stufe 1 entstehen werden

```
Kern-Plattform
  ├── Dokumenten-Import (PDF/Foto → Daten)
  ├── Order Management
  ├── Inventory
  ├── Invoice & Billing
  ├── Compliance & Reporting
  └── Chat-Integration (WhatsApp)
```

Diese Liste ist eine Prognose — die echten Module ergeben sich aus den ersten 5-10 Kunden.

## Checkliste

- [ ] 5 Architektur-Entscheidungen dokumentiert (ADRs)
- [ ] CLAUDE.md aktualisiert
- [ ] Repo-Grundstruktur angelegt
