# Phase 4 — Domain-Kern (3-4 Wochen)

**Woche:** 7-10
**Status:** Offen

## Was

Die eigentliche Business-Logik bauen — CBAM-Berechnungen, Regelwerk, Datenmodell.

## Warum

Das Herz des Produkts. Muss hundertprozentig korrekt sein. Hier entsteht der Wert.

## Output / Deliverables

Getestete Funktionen, die aus Input (Lieferung) korrekten Output (CBAM-Bedarf) machen.

## Kern-Komponenten

1. **CBAM-Datenmodell** — Waren, Lieferanten, Laender, Emissionsfaktoren, Zertifikate
2. **Berechnungslogik** — Eingebettete Emissionen, direkt/indirekt, Standardwerte vs. tatsaechliche Werte
3. **Regelwerk-Engine** — EU-Verordnung als ausfuehrbarer Code
4. **Validierung** — Eingabepruefung, Plausibilitaetschecks
5. **Reporting-Datenstruktur** — Quartalsberichte, CBAM-Deklaration

## Qualitaetsanforderungen

- 100% Testabdeckung fuer Berechnungslogik
- Referenz-Berechnungen aus EU-Dokumentation als Test-Cases
- Idempotente Berechnungen (gleicher Input = gleicher Output)

## Checkliste

- [ ] Datenmodell entworfen und migriert
- [ ] Berechnungslogik implementiert
- [ ] Unit-Tests fuer alle Berechnungen
- [ ] Regelwerk aus EU-Verordnung umgesetzt
- [ ] Validierungsregeln implementiert
- [ ] Integrationstests mit realistischen Daten
- [ ] Edge-Cases getestet (Null-Werte, Grenzfaelle)
