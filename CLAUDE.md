# AI ERP

## Projektbeschreibung
TODO: Beschreibung hier einfuegen

## Ziel
TODO: Was soll erreicht werden?

## Tech Stack
TODO: Welche Technologien?

## Deployment
- **VM:** ``
- **SSH:** `ssh -i  `
- **Pfad auf VM:** `/`


## Deploy-Workflow (Git-based)
```bash
# Lokal editieren, committen, dann:
bash deploy.sh
```
Das Script macht automatisch: git push -> VM pullt von GitHub -> Service restart -> Health-Check.

**Rollback:** `ssh -i   'cd / && git reset --hard HEAD~1'`

WICHTIG: config.yaml ist in .gitignore ??lebt NUR auf der VM mit echten Credentials. Lokal nur config.example.yaml.

## Struktur
```
AI ERP/
+-- CLAUDE.md              # Projektkontext fuer Claude
+-- CHANGELOG.md           # Versionshistorie
+-- config.example.yaml    # Config-Template (NICHT config.yaml committen!)
+-- deploy.sh              # Deploy-Script (git push + VM pull + health-check)
+-- .gitignore             # Git-Ausschluesse
+-- src/                   # Quellcode
+-- docs/                  # Dokumentation
|   +-- adding-modules.md  # Anleitung: Neue Module erstellen
+-- tests/                 # Tests
+-- modules/               # Self-contained Module
```

## Architektur-Entscheidungen
- Jedes Modul ist self-contained in modules/<name>/
- Module werden ueber eine zentrale Registry verwaltet
- config.yaml ist umgebungs-spezifisch (nicht im Repo)
- config.example.yaml ist das Template (im Repo)

## Modul-Registry
Module registrieren sich in ihrer eigenen index-Datei und werden vom Hauptprojekt importiert.
Jedes Modul enthaelt: eigenen Code, eigene Tests, eigene Docs.

## Deploy-Checkliste (jedes neue Feature)
1. [ ] Code geschrieben + getestet
2. [ ] CHANGELOG.md [Unreleased] aktualisiert
3. [ ] `bash deploy.sh` ausfuehren
4. [ ] Health-Check bestanden?

## Git-Workflow
- main: Stabiler, deploybarer Stand
- Commit direkt auf main fuer kleine Aenderungen
- Feature-Branches fuer groessere Aenderungen

## LeanHierarchy — Vault-System

Du bist der Haupt-Editor fuer alle Inhalte in `vault/`. Der Benutzer sagt dir was er braucht, du erstellst und bearbeitest Struktur + Inhalte.

### Dateien
- `vault/tree.json` — Hierarchie-Struktur (du bearbeitest diese direkt)
- `vault/nodes/<uuid>.md` — Markdown-Inhalt pro Knoten (du erstellst/bearbeitest diese)
- `vault/.claude-context.md` — Aktuelle Markierungen des Benutzers (lies diese vor jeder Aufgabe!)

### tree.json Format
```json
{
  "nodes": [
    {
      "id": "uuid-v4",
      "title": "Knoten-Titel",
      "children": [
        { "id": "uuid-v4", "title": "Kind-Knoten", "children": [] }
      ]
    }
  ]
}
```

### Regeln
1. **IDs**: Immer UUID v4 generieren (z.B. `a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d`)
2. **Max 4 Ebenen**: nodes → children → children → children (nicht tiefer)
3. **Jeder Knoten braucht eine .md-Datei**: Nach Anlegen eines Knotens in tree.json auch `vault/nodes/<id>.md` erstellen
4. **Beim Loeschen**: Knoten aus tree.json entfernen UND die zugehoerige .md-Datei loeschen
5. **Die App refresht automatisch**: Aenderungen an vault/ werden sofort in Tree und Viewer angezeigt

### Workflow
- Benutzer sagt: "Erstelle einen Bereich Authentication mit OAuth und JWT"
- Du bearbeitest `vault/tree.json` und erstellst die `.md`-Dateien
- Benutzer markiert Woerter im Viewer → Kontext erscheint in `vault/.claude-context.md`
- Du liest die Kontext-Datei und weisst genau was bearbeitet werden soll

### Sub-Claude
Funktion `sub` im PowerShell-Fenster oeffnet ein weiteres Claude-Fenster fuer Detailfragen

## Notizen
- Erstellt am: 2026-04-22 21:49
- Status: Neu
- Version: v1.0.0
