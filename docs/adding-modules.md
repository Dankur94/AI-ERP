# Module Development Guide

## Neues Modul erstellen ??Schritt fuer Schritt

### 1. Ordner anlegen
```
modules/<modul-name>/
+-- index.js (oder index.ts, main.py, etc.)
+-- README.md
+-- tests/
|   +-- <modul-name>.test.js
```

### 2. Boilerplate kopieren
Kopiere das Template aus `modules/_template/` und passe es an:
```bash
cp -r modules/_template modules/<dein-modul-name>
```

### 3. Modul implementieren
- Der Haupteinstiegspunkt ist `index.*`
- Exportiere eine klare Public API
- Halte Abhaengigkeiten minimal

### 4. Tests schreiben
- Jedes Modul hat eigene Tests in `modules/<name>/tests/`
- Mindestens: Unit-Tests fuer die Public API

### 5. Dokumentation
- Aktualisiere die `README.md` im Modul-Ordner
- Beschreibe: Was macht das Modul? Wie benutzt man es?

### 6. Registrieren
- Importiere das Modul im Hauptprojekt
- Trage es in die Modul-Registry ein (siehe CLAUDE.md)
- Fuege Config-Eintraege in config.example.yaml hinzu

### 7. Deploy
```bash
git add .
git commit -m "feat: Modul <modul-name> hinzugefuegt"
bash deploy.sh
```
