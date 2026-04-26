# Geschwindigkeit vs. Qualitaet

## Die Regel

**Tech-Debt ist ein Werkzeug, kein Fehler** — solange du bewusst entscheidest wo.

## Qualitaets-Matrix

| Bereich | Qualitaet | Grund |
|---------|-----------|-------|
| Auth/Security | Hoch | Sicherheitsluecken sind existenzbedrohend |
| CBAM-Berechnung | Hoch | Falsche Berechnungen = Bussgeld fuer Kunden |
| Audit-Trail | Hoch | Compliance-Anforderung, nicht verhandelbar |
| DSGVO | Hoch | Rechtliche Pflicht |
| API-Design | Mittel | Spaeter aendern ist aufwaendig aber machbar |
| UI/UX | Mittel | Iterativ verbesserbar |
| Admin-Tools | Niedrig | Nur internes Team nutzt es |
| Settings-Seiten | Niedrig | Funktional reicht |
| Prototypen | Niedrig | Werden sowieso ersetzt |

## Praktische Anwendung

- **Vor jedem Feature fragen:** Ist das Auth/Compliance-kritisch?
  - Ja → gruendlich, Tests, Code-Review
  - Nein → schnell, funktional, weitermachen
- **Tech-Debt tracken:** Jedes bewusste Shortcut als TODO/FIXME markieren
- **Schulden regelmaessig tilgen:** Alle 2-3 Wochen einen halben Tag Refactoring
