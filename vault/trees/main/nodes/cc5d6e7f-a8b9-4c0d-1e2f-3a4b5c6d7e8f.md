# Zeitplan & Kern-Logik

## Gesamtdauer: ~4-5 Monate bis pilotreifen MVP

## Zeitstrahl

```
Woche  1:  [Phase 0 — Desk Research          ]
Woche  2:  [Phase 1 — Requirements            ]
Woche  3:  [Phase 1 — Requirements            ]
Woche  4:  [Phase 2 — Architektur             ]
Woche  5:  [Phase 3 — Fundament               ]
Woche  6:  [Phase 3 — Fundament               ]
Woche  7:  [Phase 4 — Domain-Kern             ]
Woche  8:  [Phase 4 — Domain-Kern             ][Phase 5 — LLM (parallel)]
Woche  9:  [Phase 4 — Domain-Kern             ][Phase 5 — LLM (parallel)]
Woche 10:  [Phase 4 — Domain-Kern             ][Phase 5 — LLM (parallel)]
Woche 11:  [Phase 6 — UI                      ]
Woche 12:  [Phase 6 — UI                      ]
Woche 13:  [Phase 6 — UI                      ]
Woche 14:  [Phase 7 — Integrationen           ]
Woche 15:  [Phase 7 — Integrationen           ]
Woche 16:  [Phase 8 — Production-Readiness    ]
Woche 17:  [Phase 8 — Production-Readiness    ]
Woche 18+: [Phase 9 — Pilotkunde (laufend)    ]
```

## Kern-Logik

**Erst verstehen → dann planen → dann bauen → dann live gehen.**

1. **Verstehen** (Phase 0-1): Markt, Regeln, Nutzer kennen
2. **Planen** (Phase 2): Architektur festlegen
3. **Bauen** (Phase 3-7): Fundament → Kern → LLM → UI → Integrationen
4. **Live gehen** (Phase 8-9): Absichern → Pilotkunde → Iterieren

## Abhaengigkeiten

- Phase 1 braucht Output von Phase 0
- Phase 2 braucht Output von Phase 1
- Phase 3 braucht Output von Phase 2
- Phase 4+5 brauchen Fundament aus Phase 3
- Phase 5 kann parallel zu Phase 4 laufen
- Phase 6 braucht APIs aus Phase 4+5
- Phase 7 braucht UI-Grundgeruest aus Phase 6
- Phase 8 braucht alles davor
- Phase 9 braucht Go-Live aus Phase 8
