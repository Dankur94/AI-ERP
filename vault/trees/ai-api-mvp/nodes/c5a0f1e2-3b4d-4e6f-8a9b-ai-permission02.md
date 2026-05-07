# AI Action Policies (YAML pro Rolle)

## Prinzip

Jede Rolle (T1/T2/T3) hat eine YAML-Policy die definiert was die AI fuer diesen Nutzer tun darf.
Uebernommen von OpenShell OS1 (Deklarative Policy).

---

## T3 Policy (Endkunde)

```yaml
# policies/t3.yaml
role: t3_customer
scope: own_data_only          # Sieht nur eigene Buchungen/Daten

allow:
  - booking.create            # Termin buchen
  - booking.cancel_own        # Eigenen Termin stornieren
  - booking.view_own          # Eigene Termine sehen
  - shop.search               # Laden suchen
  - shop.view                 # Laden-Profil ansehen
  - shop.view_services        # Services/Angebote sehen
  - rating.create             # Bewertung abgeben
  - rating.view               # Bewertungen lesen
  - cart.add                  # Warenkorb befuellen
  - cart.view                 # Warenkorb ansehen
  - favorites.add             # Laden merken
  - favorites.view            # Favoriten sehen

deny:
  - payment.refund            # Kann sich nicht selbst Geld zurueckgeben
  - shop.edit                 # Kann Laden nicht aendern
  - booking.view_others       # Sieht keine fremden Buchungen
  - customer.*                # Kein Zugriff auf Kundenverwaltung
  - settings.*                # Kein Zugriff auf Einstellungen

confirm_required:
  - payment.create            # "Soll ich 150 HKD bezahlen?" → Bestaetigung
  - booking.cancel_own        # "Termin morgen 14:00 stornieren?" → Bestaetigung
```

---

## T2 Policy (Shop-Owner)

```yaml
# policies/t2.yaml
role: t2_shop_owner
scope: own_shop_only          # ALLES nur fuer eigenen Laden (shop_id erzwungen)

allow:
  - booking.*                 # Alle Buchungs-Aktionen
  - booking.view_all          # Alle Buchungen seines Ladens
  - customer.view             # Kunden sehen
  - customer.view_history     # Kundenhistorie sehen
  - customer.message          # Einzelnen Kunden anschreiben
  - settings.edit             # Laden-Einstellungen aendern
  - settings.edit_services    # Services bearbeiten
  - settings.edit_hours       # Oeffnungszeiten aendern
  - payment.view              # Zahlungen sehen
  - payment.view_stats        # Umsatz-Statistiken
  - rating.view               # Bewertungen lesen
  - rating.respond            # Auf Bewertungen antworten
  - promo.create              # Rabattaktion erstellen
  - promo.edit                # Rabattaktion aendern

deny:
  - payment.create_manual     # Kann keine Fake-Zahlung erzeugen
  - payment.refund_bulk       # Kein Massen-Refund
  - customer.export_all       # Kein Massen-Export (PDPO)
  - customer.delete           # Kunden loeschen braucht Consent-Flow
  - settings.delete_shop      # Laden loeschen braucht Support
  - settings.api_keys         # Kein Zugriff auf technische Keys

confirm_required:
  - settings.edit_prices      # "Preise aendern auf X?" → Bestaetigung
  - customer.message_all      # "Nachricht an alle 200 Kunden?" → Bestaetigung
  - promo.create              # "Rabatt 20% fuer alle Services?" → Bestaetigung
  - booking.cancel_customer   # "Termin von Kunde X stornieren?" → Bestaetigung
```

---

## T1 Policy (Developer)

```yaml
# policies/t1.yaml
role: t1_developer
scope: own_api_key_only       # Nur Zugriff auf Daten die zum API-Key gehoeren

allow:
  - api.*                     # Voller API-Zugriff (innerhalb Scope)
  - webhook.create            # Webhooks registrieren
  - webhook.delete            # Webhooks loeschen
  - module.list               # Verfuegbare Module sehen
  - module.enable             # Modul aktivieren
  - module.disable            # Modul deaktivieren

deny:
  - system.*                  # Kein Zugriff auf System-Internals
  - customer.export_raw       # Kein Roh-Export (nur ueber API mit Rate-Limit)
  - settings.billing          # Kein Zugriff auf Billing anderer

rate_limit:
  requests_per_minute: 60     # Standard Rate-Limit
  burst: 100                  # Burst erlaubt
```

---

## Wie Policies geladen werden

```python
# Pseudocode
def load_policy(role: str) -> Policy:
    """Laedt Policy aus YAML. Cached im Memory."""
    path = f"config/policies/{role}.yaml"
    return yaml.safe_load(open(path))
```

- Policies liegen in `config/policies/`
- Werden beim Gateway-Start geladen
- Koennen zur Laufzeit neu geladen werden (OS3 — Live Policy Updates)
- Jede Aenderung wird im Audit-Log festgehalten

## Wildcard-Regeln

- `booking.*` → erlaubt alle Actions die mit `booking.` beginnen
- Explizites `deny` ueberschreibt immer `allow` (Deny wins)
- Was nicht in `allow` steht ist automatisch verboten (Deny-by-Default)

## Validierung

Policies werden beim Laden validiert:
- Keine Action darf gleichzeitig in `allow` und `deny` stehen
- Jede Action muss einem registrierten Modul-Intent entsprechen
- `scope` muss gesetzt sein (kein "alles sehen" moeglich)
