# Stufe 1 — Sicherheits-Checkliste (Minimum)

Was wir in Stufe 1 absichern muessen. Kein Bankstandard, aber das Minimum.

---

## Was wir schuetzen

Rechnungen, Zahlungen, Geschaeftsdaten kleiner Firmen. Sensibel, aber nicht lebenskritisch.

## Schlimmste Faelle

| Risiko | Was passiert | Schutz |
|---|---|---|
| Jemand kommt auf den Server | Liest alle Kundendaten | SSH-Key, kein Passwort-Login, Updates |
| API-Keys gestohlen | Stripe-Konto missbraucht, Claude-Kosten | Keys nie im Code, nur config.yaml auf VM |
| Manipulierte PDF | Server fuehrt fremden Code aus | Eingaben pruefen (Typ, Groesse, Format) |
| Kunde sieht fremde Daten | David sieht Michelles Rechnungen | shop_id bei JEDER Abfrage (L3) |
| Server faellt aus | Niemand kann arbeiten | Backups, taeglich, testen |

---

## Checkliste

### KERN-Code

- [ ] Passwoerter gehasht (bcrypt), nie Klartext
- [ ] Login-Versuche begrenzt (5 Versuche, dann 15 Min Sperre)
- [ ] Session-Token mit Ablaufzeit (24h)
- [ ] Jede DB-Abfrage filtert nach shop_id (im KERN erzwungen, nicht pro Modul)
- [ ] Eingabe-Validierung: alles vom Nutzer ist nicht vertrauenswuerdig
- [ ] PDFs pruefen vor Verarbeitung (Dateityp, Groesse, Format)
- [ ] Kein rohes SQL aus Nutzereingaben (SQLAlchemy macht es richtig)

### Server / VM

- [ ] SSH nur mit Key, kein Passwort-Login
- [ ] Root-Login deaktiviert
- [ ] Firewall: nur Port 443 (HTTPS) und SSH offen
- [ ] Betriebssystem regelmaessig updaten
- [ ] Python-Pakete pruefen (pip audit)
- [ ] HTTPS mit Let's Encrypt (kostenlos)

### Secrets

- [ ] Kein einziger Key im Code
- [ ] config.yaml nur auf VM, nie im Git
- [ ] .gitignore enthaelt config.yaml, .env, alles Sensitive
- [ ] Wenn ein Key auf GitHub landet: sofort austauschen

### Datenbank

- [ ] Taeglich Backup (SQLite = eine Datei kopieren)
- [ ] Backup an zweiten Ort
- [ ] Einmal pro Woche testen: Backup zurueckspielen
- [ ] SQLite-Datei nicht ueber Web erreichbar

### Adapter (Externe Dienste)

- [ ] Stripe: Ausgabenlimit setzen
- [ ] Claude API: Spending-Limit setzen
- [ ] Twilio: nur bestimmte Nummern erlauben
- [ ] Jeder gestohlene Key hat begrenzten Schaden

---

## Merksatz

Die meisten Angriffe kommen nicht durch clevere Hacks, sondern durch einfache Fehler: Passwort 123456, API-Key auf GitHub, Update nicht installiert.
