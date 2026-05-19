# HKSTP Ideation Programme — Bewerbung Elli

Stand: 2026-05-19. Cohort 26-22 (September 2026 Intake).

## Status: EINGEREICHT ✅

Eingereicht am **18. Mai 2026** (vor Deadline 12:00 Noon).
Ergebnis erwartet: **~August 2026**.

## Elli = AI-powered OS fuer Local Commerce

### Die OS-Metapher

Elli ist kein einzelnes Feature oder eine App — Elli ist ein **Operating System fuer lokalen Handel**.
Wie Windows Hardware abstrahiert und Apps eine einheitliche Laufzeitumgebung bietet,
abstrahiert Elli lokale Geschaefte und bietet Kunden eine einheitliche Interaktionsschicht.

| OS Konzept | Elli Equivalent |
|---|---|
| Kernel | Gateway (Hub-and-Spoke, ein Eingang) |
| System Services | Module (Booking, Payment, Deals, Wayfinding...) |
| Device Drivers | Adapter (Stripe, Twilio, Firebase, Google Maps...) |
| Applications | Shops (jeder Shop = eine "App" auf der Plattform) |
| Shell / CLI | Elli AI (natuerliche Sprache → Intent → Aktion) |
| File System | Memory 4 Schichten (Session → User → Shop → Platform) |
| User Permissions | Action Levels L1-L4 (deny-by-default, AI kann nicht overriden) |
| Process Isolation | shop_id Isolation (kein Shop sieht Daten anderer Shops) |
| User | T3 Endkunde |
| App Developer | T2 Shop-Owner (baut seinen "App" via Dashboard) |
| Sysadmin | T1 Plattform-Admin |

### Warum OS und nicht "App" oder "Plattform"

1. **Abstraktionsschicht**: Elli versteckt Komplexitaet — T3 sagt "buche mir Haarschnitt", Elli orchestriert Service-Suche, Verfuegbarkeitspruefung, Buchung, Payment, Notification. Wie ein OS System Calls abstrahiert.
2. **Erweiterbar**: Neue Module (= neue System Services) koennen angedockt werden ohne bestehende zu aendern. Hub-and-Spoke.
3. **Multi-Tenant**: Jeder Shop laeuft isoliert (wie Prozesse in einem OS), teilt aber die Infrastruktur.
4. **Driver-Modell**: Adapter fuer externe APIs sind austauschbar (Mock → Real), identisches Interface. Wie Device Drivers.
5. **L2→L3 Skalierung**: Gleicher Kernel steuert spaeter auch physische Aktionen (Drohnen, Roboter, IoT) — CreatorPort und FamHub als L3-Piloten.

### Framing je nach Audience

| Audience | Framing | Sprache |
|---|---|---|
| HKSTP / Investoren | "AI-powered Local Commerce OS" | Infrastruktur, R&D, Skalierbarkeit |
| Cyberport | "AI Operating System for SME Digitisation" | Innovation, Tech-Tiefe |
| Shop-Owner (T2) | "Dein digitaler Laden-Assistent" | Einfach, kein Technik-Jargon |
| Endkunde (T3) | "Elli" | Merkt nicht dass OS dahinter |
| Developers (T1) | "Local Commerce Runtime" | API, SDK, Build-on-top |

## Programm-Ueberblick

- 1-Jahr Startup-Support fuer Early-Stage Entrepreneurs in HK
- Seed Funding: bis zu **HKD 100,000** (3 Tranchen, milestone-basiert)
- **Kein Equity** abgeben
- Mentorship, Training (Pflicht!), Networking
- Nach Ideation → HKSTP Incubation moeglich
- Bewerbungsrunden: Januar, Mai, September

## Bewerber

**Company Applicant** — Space of Possibilities Ltd.
- Gruendung: 30. Oktober 2025 (< 2 Jahre ✓)
- BR: gueltig ✓
- PIC: Gruender = Shareholder (NNC1) ✓
- Dokumente eingereicht: CI + BR + NNC1 ✓

## 4 Assessment-Kriterien (Panel)

1. **Team Competency** — Solo-Founder, RWTH B.Sc. Industrial Engineering, komplettes MVP in 10 Tagen gebaut
2. **Business Development Potential** — 29 Shops gemappt, Pilotregion Riviera Gardens, Live-Produkt
3. **Innovativeness** — Einzige AI-native + Cross-Shop Plattform in HK, OS-Architektur
4. **Research & Development** — "Deterministic output from probabilistic AI" als Forschungsfrage

## Eingereichte Unterlagen

- [x] Pitch Deck (12 Slides, PPT) — `docs/hkstp-pitch-deck-filled.pptx`
- [x] Pitch Video (2.5-3.5 Min, Daniel persoenlich, Live-Demo)
- [x] Certificate of Incorporation (CI)
- [x] Business Registration (BR)
- [x] NNC1 (Shareholder-Nachweis)

Textvorlage Pitch Deck: `docs/hkstp-ideation-pitch-deck.md`
Video-Script: `docs/hkstp-powerpoint-script.md`

## Pitch Deck Inhalt (12 Slides)

| Slide | Sektion | Kern-Aussage |
|---|---|---|
| 1 | Cover | Elli — AI-powered OS for Local Commerce |
| 2 | Project Summary | 40-Wort Intro, RetailTech + App/Software, HK hat 300K SMEs ohne Plattform |
| 3a | AI Impact Layers | L1 Information → L2 Transaction (ELLI) → L3 Physical (CreatorPort/FamHub) |
| 3b | Core Features | 7 Features: AI Chat, Cross-Shop Discovery, Booking, Payments, Wayfinding, Deals, Dashboard |
| 3c | Technology | AI Orchestrator (11 Tools), Intent Detection (6 Signale), Action Levels (L1-L4), Indoor Nav |
| 4a | R&D Achievements | 30k LOC, 624 Tests, 111 Endpoints, 10 Module, 9 Adapter — in 10 Tagen solo gebaut |
| 4b | Technologies Developed | 7 Eigenentwicklungen: Orchestrator, Persona Lab, Intent-Mode, Graph Position, Floor Plan Editor, Action Levels, Smart Clarification |
| 4c | R&D Plan (12 Monate) | Q1 Payments/Cantonese → Q2 Public APIs → Q3 ERP → Q4 Hardware |
| 5 | Competitive Analysis | Meituan (China), Set Sail (HK), Vendasta (Canada) — Elli einzige AI-native + Cross-Shop |
| 6 | Perceptual Mapping | Achsen: AI Determinism × Price → Elli top-left (beste Position) |
| 7 | Sales & Marketing | TAM 300K → SAM 50K → SOM Year 1: 29 Shops, Door-to-door, Free Pilot |
| 8 | Business Model | Pay-per-Use (WhatsApp-Modell), Breakeven ~7 Shops |
| 9 | Schedule | 4 Quartale: 5→20→40→100+ Shops, 3 Tranchen HKSTP |
| 10 | Team | Daniel Kurth (RWTH Aachen), Ananya Singh (Scientific Advisor) |
| 11 | Why HKSTP | Mentorship, Credibility, Networking, Training, Ecosystem |
| 12 | Live Demo | elli.com.hk (T3), /dashboard (T2), /review (T1) |

## Strategische Entscheidungen im Antrag

### Revenue Model: Pay-per-Use
- Shift von SaaS-Subscription zu WhatsApp Business API Modell
- Tiers: Free (Pilot) → Basic (HK$0) → Pro (HK$299) → Premium (HK$599)
- Zusaetzlich: 2-3% Transaction Fees, Promoted Listings
- Breakeven: ~7 aktive Shops (~HK$1,000/mo Kosten)

### R&D Framing: Deterministic Output from Probabilistic AI
- Kern-Forschungsfrage: Wie bekommt man zuverlaessige Transaktionen aus nicht-deterministischem LLM?
- Systematisches Testen: 60 Szenarien × 12 Personas × 4 Action Severity Levels
- Pilot: 29 Shops + 3% von 17,278 Riviera Gardens Residents
- Forschungsfokus: **Security** (Datenschutz, Prompt Injection), **Safety** (AI Eskalation), **Reliability** (konsistente Antworten), **Stability** (gleichzeitige Last)

### Competitive Positioning
- Echte Wettbewerber: Meituan (China), Set Sail (HK), Vendasta (Canada)
- Nicht: OpenRice/Google Maps/Inline (zu unterschiedlich)
- Perceptual Map: AI Determinism × Price → Elli unique top-left
- USP: Einzige Plattform die AI-native UND Cross-Shop UND lokal ist

### Technology Roadmap (12 Monate)
- **Q1** (Sep-Nov 2026): Booking/Payments stabil, Cantonese NLP, Stripe live, WhatsApp Notifications
- **Q2** (Dec-Feb 2027): Public APIs (KMB, HK Map), Recommendation Engine, Analytics v2
- **Q3** (Mar-May 2027): Business Modules (ERP, Analytics, Website Builder), Native Android
- **Q4** (Jun-Aug 2027): Hardware + Big Players, iOS, Predictive Demand, API Marketplace

### 3 Produkte unter einem Dach (L2→L3)
- **Elli**: AI Consumer Platform (L2 Transaction) — elli.com.hk — LIVE
- **CreatorPort**: AI & Robotics Education (L3 Physical) — Drohnen, Roboter fuer Kids
- **FamHub**: Smart Parenting (L3 Physical) — ESP32 Sensoren, Baby-Logging

## Admission Process Timeline

| Schritt | Wann | Status |
|---|---|---|
| Application Submission | 18. Mai 2026, 12:00 | ✅ DONE |
| Pre-Screening | ~Juni-Juli 2026 | WARTEND |
| Admission Panel Pitch | ~Juli-August 2026 | Falls shortlisted |
| Due Diligence Meeting | ~August 2026 | Detail-Fragen |
| Result Announcement | ~August 2026 | |
| Bei Aufnahme: Tranche 1 | ~September 2026 | Development Plan mit HKSTP erstellen |

## Funding-Auszahlung

- One-Year Development Plan wird mit HKSTP erstellt
- HKD 100,000 in 3 Tranchen bei Milestone-Erreichung:
  - Milestone 1: Problem-Solution Fit validiert
  - Milestone 2: Prototyp + Market Traction
  - Milestone 3: Business-ready
- Alle Trainings/Assignments muessen erledigt werden (Pflicht!)

## Parallel-Aktionen (nicht auf HKSTP warten)

| Prio | Aktion | Status |
|---|---|---|
| 1 | Door-to-door Shops in Riviera Gardens ansprechen | Offen |
| 2 | Stripe live payments aktivieren | Offen |
| 3 | Volunteer Developers rekrutieren | Offen |
| 4 | CreatorPort Workshops starten (Eltern → Elli Funnel) | Offen |
| 5 | Cyberport CCMF + Incubation vorbereiten (Deadline ~03.08.2026) | Ab Juni |

## Naechste Fundings

| Programm | Deadline | Aktion |
|---|---|---|
| Cyberport CCMF | ~03.08.2026 | Ab Juni vorbereiten, "AI-powered Local Commerce OS" Framing |
| Cyberport Incubation | ~03.08.2026 | Parallel mit CCMF einreichen |
| HKSTP Incubation | Rolling | Einreichen falls Ideation erfolgreich |

## Elli als OS — Zahlen zum Zeitpunkt der Bewerbung

```
Kernel (Gateway):        1 Eingang, Hub-and-Spoke
System Services:        10 Module (Profile, Booking, Payment, Notification, Memory, Modulbaukasten, QR, Reviews, Wayfinding, Content)
Drivers (Adapter):       9 (Stripe, PayMe, Octopus, FPS, Firebase, Claude AI, Google OAuth, Google Maps, Twilio SMS)
Apps (Shops):           29 geseeded (Riviera Gardens), 58 Services
Shell (AI):              1 Orchestrator, 11 Tools, 6 Intent-Signale, 12 Personas
Security:               Action Levels L1-L4, deny-by-default, OTP, Rate Limiting
Test Suite:            624 Tests
API Surface:           111 Endpoints
Codebase:             ~30k Lines
Build Time:            10 Tage, 1 Entwickler
```

## Referenzen

- HKSTP Ideation: https://www.hkstp.org/en/programmes/ideation
- Portal: https://partnersconnect.hkstp.org/user-guide/
- Pitch Deck (Text): `docs/hkstp-ideation-pitch-deck.md`
- Pitch Deck (PPT): `docs/hkstp-pitch-deck-filled.pptx`
- Video Script: `docs/hkstp-powerpoint-script.md`
- Session (Planung): `docs/sessions/2026-05-13-hkstp-ideation.md`
- Session (Pitch Deck): `docs/sessions/2026-05-15-hkstp-pitch-deck.md`
- Session (Einreichung): `docs/sessions/2026-05-18.md`
