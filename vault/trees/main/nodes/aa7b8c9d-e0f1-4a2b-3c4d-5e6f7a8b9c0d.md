# Phase 5 — LLM-Integration (2-3 Wochen, teils parallel zu Phase 4)

**Woche:** 8-10
**Status:** Offen

## Was

Claude/AI in das Produkt einbauen — Dokumentenverarbeitung, Extraktion, Klassifikation.

## Warum

Das Differenzierungsmerkmal zum Markt. Kein anderes CBAM-Tool nutzt LLMs so tief.

## Output / Deliverables

PDFs rein → strukturierte Daten raus. Prompts, Validierungen, Fallbacks.

## Kern-Features

1. **Dokumenten-Upload & OCR** — PDF, Bilder, Scans verarbeiten
2. **Datenextraktion** — Lieferanteninfos, Warenmengen, Emissionsdaten aus Dokumenten ziehen
3. **Klassifikation** — Waren automatisch KN-Codes zuordnen
4. **Prompt Engineering** — Robuste Prompts fuer konsistente Ergebnisse
5. **Validierung & Confidence** — LLM-Output pruefen, Confidence-Scores
6. **Fallback-Logik** — Wenn LLM unsicher ist → manueller Review-Workflow
7. **Human-in-the-Loop** — Nutzer korrigiert/bestaetigt LLM-Vorschlaege

## Qualitaetsanforderungen

- Extraktion mind. 85% korrekt (gemessen an Test-Set)
- Klare Confidence-Anzeige fuer Nutzer
- Graceful Degradation wenn API nicht verfuegbar
- Kosten-Monitoring pro Anfrage

## Checkliste

- [ ] Dokumenten-Upload implementiert
- [ ] OCR/Textextraktion funktioniert
- [ ] Prompts fuer Datenextraktion entwickelt und getestet
- [ ] KN-Code-Klassifikation implementiert
- [ ] Confidence-Scoring eingebaut
- [ ] Fallback/Manual-Review-Workflow
- [ ] Kosten-Tracking pro API-Call
- [ ] Test-Set mit mind. 20 realen Dokumenten
