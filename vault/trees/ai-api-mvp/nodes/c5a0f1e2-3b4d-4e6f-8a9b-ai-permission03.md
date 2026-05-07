# AI Action Levels (Deterministisches Safety Gate)

## Was es ist

Eine zweite Sicherheitsschicht **nach** dem Permission Gate, **vor** der Tool-Ausfuehrung.
Waehrend der Permission Gate prueft ob eine Rolle eine Action darf (ALLOW/DENY),
pruefen die Action Levels **wie** die Action ausgefuehrt wird.

```
User → AI → [Permission Gate: darf er?] → [Action Levels: wie ausfuehren?] → Tool Executor
                    ALLOW/DENY                   L1/L2/L3/L4
```

## Warum noetig

Das Permission Gate kennt nur ALLOW/DENY/CONFIRM.
Aber "CONFIRM" ist nicht differenziert genug:

- "Zeig meine Buchungen" braucht keine Bestaetigung (L1)
- "Buche einen Termin" braucht 1-Klick Bestaetigung (L2)
- "Storniere alle Buchungen" braucht Warning + Details (L3)
- "Loesch meinen Account" darf gar nicht per Chat gehen (L4)

## Die 4 Levels

| Level | Name | Verhalten | User-Erlebnis |
|---|---|---|---|
| L1 READ | Sofort | AI fuehrt aus, zeigt Ergebnis | Instant, kein Klick |
| L2 CONFIRM | 1-Klick | AI zeigt Preview → User bestaetigt | Schnell, sicher |
| L3 WARN | Warning | AI zeigt Warning + betroffene Items | Bewusste Entscheidung |
| L4 BLOCK | Gesperrt | Nur ueber klassische UI | Schutz vor Fehlern |

## 5 Regeln bestimmen das Level

```python
def calculate_level(action, params):
    level = 1  # Start: READ

    if action.is_write:        level = max(level, 2)  # CREATE/UPDATE
    if action.affects_others:  level = max(level, 3)  # Blast Radius
    if not action.is_reversible: level = max(level, 3)  # Nicht rueckgaengig
    if action.involves_money:  level = max(level, 2)
        if amount > 500 HKD:   level = max(level, 3)
        if amount > 5000 HKD:  level = 4              # Hard Floor
    if action.is_destructive and action.is_permanent:
        level = 4                                      # Hard Floor
```

## Dynamische Eskalation

Manche Tools aendern ihr Level je nach Parametern zur Laufzeit:

| Tool | Normal | Eskalation | Neues Level |
|---|---|---|---|
| `update_service` | L2 | + Preis aendert sich | L3 |
| `change_booking_status` | L2 | + status=cancelled | L3 |
| `start_payment` | L2 | + amount > 500 HKD | L3 |
| `start_payment` | L2 | + amount > 5000 HKD | L4 |

Eskalation geht **nur nach oben**, nie nach unten.

## Verteilung (72 Actions)

```
L1 READ    ████████████████████████████████████  38 (55%)
L2 CONFIRM ████████████████████                  20 (29%)
L3 WARN    ████████                               10 (14%)
L4 BLOCK   ██                                      4 (2%)
```

55% aller Actions fuehrt die AI sofort aus. Fuehlt sich frei an,
aber bei den kritischen 14% greift der Schutz.

## Real-World Analogien

| Analogie | L1 | L2 | L3 | L4 |
|---|---|---|---|---|
| **Handy** | Internet nutzen | Kamera erlauben | Standort jedes Mal | SIM loeschen |
| **Bank** | Kontostand | Kontaktlos <50€ | Ueberweisung + TAN | Filiale noetig |
| **Tesla** | Spur halten | Spurwechsel + Blinker | Ausfahrt + Lenkrad | Rote Ampel |
| **YouTube** | Stats sehen | Video hochladen | Post loeschen | Kanal loeschen + 7d |

## Position im Stack

```
src/core/action_levels.py          ← DIESE Komponente
├── ActionLevel (IntEnum L1-L4)
├── ActionConfig (Dataclass pro Tool)
├── EscalationRule (Dynamische Bedingungen)
├── T2_ACTION_LEVELS (dict)
├── T3_ACTION_LEVELS (dict)
├── calculate_level(role, tool, params) → (level, config, reason)
└── get_action_config(role, tool) → ActionConfig

src/modules/modulbaukasten/
├── tool_executor.py               ← Prueft Level vor Ausfuehrung
│   └── execute_tool(..., confirmed=True)
├── chat_service.py                ← Confirmation Flow
│   └── confirm_action()           ← Nach User-Bestaetigung
├── routes.py                      ← POST /chat/{id}/confirm (T2)
└── t3_routes.py                   ← POST /chat/{id}/confirm (T3)

web/t2/src/components/
├── ConfirmationCard.vue           ← Preview + Bestaetigen/Abbrechen
├── ActionBlockedCard.vue          ← Blockiert-Meldung + Redirect
└── RichBlock.vue                  ← Rendert confirmation_request + action_blocked

web/t3/src/components/
├── ConfirmationCard.vue           ← (gleich, orange Theme)
├── ActionBlockedCard.vue          ← (gleich, orange Theme)
└── RichBlock.vue                  ← (gleich)
```

## Zusammenspiel Permission Gate + Action Levels

```
Request kommt rein:
│
├── 1. Auth: Wer bist du? (JWT/Session)
├── 2. Permission Gate: Darfst du das? (YAML Policy)
│     └── DENY → Sofort abgelehnt
│     └── ALLOW → Weiter zu Schritt 3
├── 3. Action Level: Wie ausfuehren? (action_levels.py)
│     └── L1 → Sofort ausfuehren
│     └── L2 → Preview + Bestaetigen-Button
│     └── L3 → Warning + Details + Bestaetigen
│     └── L4 → Blockiert, Redirect zu UI
├── 4. Tool Executor: Fuehrt aus (deterministisch)
└── 5. AI: Fasst Ergebnis zusammen (probabilistisch)
```

## Status

- Backend: FERTIG — action_levels.py, tool_executor.py, chat_service.py, 42 Tests
- Frontend: FERTIG — ConfirmationCard.vue, ActionBlockedCard.vue, confirm Routes (T2+T3), 5 Tests
- 404 Tests total, alle gruen
- Progressive Trust (User-konfigurierbare Levels): SPAETER
