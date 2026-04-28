# AI ERP

## WICHTIG — Vor jeder Arbeit lesen

Lies diese Datei KOMPLETT bevor du antwortest oder Code schreibst.
Lies danach: @vault/trees/main/nodes/e9f0a1b2-c3d4-4e5f-6a7b-8c9d0e1f2a3b.md (Master-Briefing)
Lies danach: CHANGELOG.md (Was ist gebaut)
Lies danach: docs/sessions/ (neueste Datei — was wurde zuletzt gemacht)

## Produkt

**Dokument rein → extrahieren → abgleichen → reporten → warnen. Eine Pipeline, ein Tool, fuer kleine Firmen (5-15 Leute) in HK.**
Kein Wettbewerber hat die volle Pipeline fuer KMU. Wir schliessen diese Luecke.

## Leitprinzip

Heute fuer Stufe 1 (Custom) bauen. Nicht fuer Stufe 3-4.
Pflicht: L1 (kein Fork), L2 (geteiltes Datenmodell), L3 (Isolation), L4 (progressiv).
Verboten: L6 (API-Version), L9 (Sandbox), L11 (Queues), L15 (4-Layer-Memory).

## Struktur

```
AI ERP/
├── CLAUDE.md           ← Diese Datei
├── CHANGELOG.md        ← Was ist gebaut
├── vault/              ← Wissen (Tree + Viewer, NICHT Software)
├── src/                ← Software (das Produkt)
│   ├── api/            ← Backend
│   ├── web/            ← Frontend
│   └── shared/         ← Geteilte Typen
├── docs/
│   ├── domain/         ← Fachwissen (@-Referenz)
│   └── sessions/       ← Session-Handoffs
└── tests/              ← Tests
```

## Code-Konventionen

- Python mit Type Hints (strict)
- Keine print() in Production
- Jede Funktion braucht Type Hints
- Keine Secrets im Code
- Commit: feat: / fix: / refactor:

## LeanHierarchy — Vault-System

Du bist der Haupt-Editor fuer alle Inhalte in `vault/`.

### Dateien
- `vault/trees.json` — Registry: aktiver Tree + Liste aller Trees
- `vault/trees/<tree-id>/tree.json` — Hierarchie-Struktur pro Tree
- `vault/trees/<tree-id>/nodes/<uuid>.md` — Markdown-Inhalt pro Knoten
- `vault/.claude-context.md` — Markierungen des Benutzers (lies vor jeder Aufgabe!)

### Regeln
1. IDs: Immer UUID v4
2. Max 4 Ebenen
3. Jeder Knoten braucht eine .md-Datei
4. Beim Loeschen: tree.json UND .md-Datei
5. App refresht automatisch
6. Mehrere Trees moeglich — jeder hat eigene nodes/ und .highlights.json

## Session-Ende Pflicht

Am Ende jeder Session → `docs/sessions/YYYY-MM-DD.md`:
Was gemacht, offene Entscheidungen, naechste Schritte.

## Deploy

```bash
bash deploy.sh
```
config.yaml lebt NUR auf der VM. Lokal nur config.example.yaml.

## Git-Workflow

- main: Stabiler Stand
- Commit direkt auf main fuer kleine Aenderungen
- Feature-Branches fuer groessere Aenderungen
