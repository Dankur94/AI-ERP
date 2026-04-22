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

## Notizen
- Erstellt am: 2026-04-22 21:49
- Status: Neu
- Version: v1.0.0
