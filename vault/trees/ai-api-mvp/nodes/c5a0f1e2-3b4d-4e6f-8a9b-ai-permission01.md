# AI Permission Gate (Deny-by-Default)

## Was es ist

Die Sicherheitsschicht zwischen AI-Intent und Modul-Ausfuehrung. Die AI parsed was der Nutzer will,
aber der **Permission Gate** entscheidet ob die Aktion erlaubt ist.

```
User ──chat──→ AI (Intent Parser) ──→ [PERMISSION GATE] ──→ Modul (Execution)
                                            │
                                     Prueft: Darf er das?
                                     Policy: policies/t3.yaml
```

## Warum es KERN ist

Ohne Permission Gate koennte die AI:
- Fremde Buchungen stornieren
- Preise ohne Bestaetigung aendern
- Daten anderer Laeden lesen
- Zahlungen ohne Consent ausloesen

→ Permission Gate ist KERN, nicht Modul. Es steht im Gateway.

## Wie es funktioniert

### 1. AI parsed Intent

```
Nutzer:  "Storniere meinen Termin morgen"
AI:      → Intent: booking.cancel_own
         → Params: {date: tomorrow, user_id: xyz}
```

Die AI erkennt NUR definierte Actions. Sie kann keine neuen erfinden.

### 2. Permission Gate prueft

```python
# Pseudocode
def check_permission(user, intent, params):
    policy = load_policy(user.role)         # policies/t3.yaml

    # 1. Ist die Action ueberhaupt erlaubt?
    if intent in policy.deny:
        return DENY

    if intent not in policy.allow:
        return DENY                          # Deny-by-Default (NC1)

    # 2. Scope-Check: Darf er auf DIESE Daten?
    if not scope_check(user, params):
        return DENY                          # shop_id Isolation

    # 3. Braucht es Bestaetigung?
    if intent in policy.confirm_required:
        return CONFIRM                       # AI fragt zurueck

    return ALLOW
```

### 3. Ergebnis

| Ergebnis | Was passiert |
|---|---|
| **ALLOW** | Action wird ausgefuehrt, AI zeigt Ergebnis |
| **DENY** | AI sagt: "Das kann ich leider nicht fuer dich tun" |
| **CONFIRM** | AI fragt: "Soll ich X wirklich tun?" → wartet auf Ja/Nein |

## Die 5 Sicherheitsschichten

| # | Schicht | Was sie tut | Schuetzt gegen |
|---|---|---|---|
| 1 | **Intent Whitelist** | AI erkennt nur definierte Actions | AI "erfindet" Faehigkeiten |
| 2 | **Permission Gate** | RBAC + Scope Check (shop_id) | Unbefugter Zugriff |
| 3 | **Action Levels** | L1-L4 Gate (Read/Confirm/Warn/Block) | AI fuehrt kritische Actions ohne Consent aus |
| 4 | **Confirm Loop** | L2/L3 Actions brauchen User-Klick | Versehentliche Ausfuehrung |
| 5 | **Audit Log** | Jede Action geloggt (wer/was/wann/erlaubt?) | Nachvollziehbarkeit |

→ Siehe auch: **AI Action Levels (L1-L4 Safety Gate)** — eigener Node mit Details.

## Unterschied zu NemoClaw

| NemoClaw (NVIDIA) | Unser Permission Gate |
|---|---|
| Schuetzt **OS** vor Agent | Schuetzt **Business-Logik** vor Agent |
| Container + Kernel-Level Sandbox | Application-Level im Gateway |
| Agent hat Filesystem-Zugriff | Agent hat nur definierte Actions |
| OpenShell Runtime noetig | Nur YAML-Policies + Gateway-Code |

```
NemoClaw:   Agent → [Container + Kernel Policy] → System
Wir:        User → AI → [Permission Gate + YAML Policy] → Module
```

Selbe Prinzipien (Deny-by-Default, deklarativ, Audit), leichtere Implementierung
weil wir die Runtime kontrollieren.

## Was wir NICHT brauchen

- **Kein Kernel-Level Sandboxing** — AI ruft keine Systembefehle auf
- **Kein Container pro Session** — Gateway ist der Kontrollpunkt
- **Kein Privacy Router (Stufe 1)** — keine sensiblen Daten im Prompt (nur Intent)

## Position im Stack

```
src/
├── gateway/
│   ├── routes.py          ← Empfaengt Request
│   ├── auth.py            ← Wer bist du?
│   ├── permission_gate.py ← DIESE Komponente
│   └── ai_router.py       ← Leitet Intent an AI / Modul
├── core/
│   └── policies/
│       ├── t3.yaml        ← Endkunde-Rechte
│       ├── t2.yaml        ← Shop-Owner-Rechte
│       └── t1.yaml        ← Developer-Rechte
```
