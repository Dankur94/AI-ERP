# Begleit-Prinzipien

Keine Phasen, sondern laufende Prinzipien die ueber den gesamten Entwicklungszeitraum gelten.

## Prinzip A: Geschwindigkeit vs. Qualitaet

Unwichtiges schnell, Wichtiges gruendlich. Tech-Debt bewusst waehlen.

**Niemals schludern bei:**
- Authentication & Authorization
- CBAM-Berechnungslogik
- Compliance & Audit-Trail
- Datenschutz / DSGVO

**Darf hacky sein:**
- Settings-UI
- Admin-Panels
- Interne Tools
- Prototyping-Code (der spaeter ersetzt wird)

## Prinzip B: Meta-Ebene

- Dokumentation parallel schreiben, nicht nachtraeglich
- Runbooks fuer Notfaelle anlegen
- Woechentliches Review des eigenen Codes und der Entscheidungen
- CHANGELOG.md bei jedem Feature aktualisieren
