# Meta-Ebene & Dokumentation

## Warum parallel dokumentieren?

Dokumentation die erst am Ende geschrieben wird, wird nie geschrieben. Oder ist falsch.

## Laufende Dokumentations-Aufgaben

### Bei jedem Feature
- CHANGELOG.md aktualisieren ([Unreleased]-Section)
- ADR schreiben wenn architekturrelevant
- Inline-Kommentare nur wo Logik nicht offensichtlich

### Woechentlich
- Code-Review des eigenen Codes der letzten Woche
- Entscheidungen hinterfragen: "Wuerde ich das nochmal so machen?"
- vault/ aktualisieren wenn sich Erkenntnisse aendern

### Bei jedem Deploy
- Runbook pruefen: Ist es noch aktuell?
- Monitoring-Dashboards checken: Sehen wir was wir sehen muessen?

## Runbook-Themen (ab Phase 3)

1. DB ist nicht erreichbar
2. LLM-API antwortet nicht / Timeout
3. Speicherplatz voll
4. Nutzer meldet falsche Berechnung
5. Backup-Restore durchfuehren
6. Neuen Tenant anlegen
7. Feature-Flag aendern
