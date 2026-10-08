# Changelog

Todos los cambios notables de este proyecto se documentan acá, siguiendo
[Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/).

## [2.0.0] - 2026-10-08

### Agregado

- Renombrado de `flight-search-ar` a `travel-search-ar`.
- Sección de hoteles: Google Hotels, Anduin API (categoría `hoteles`),
  Promociones Aéreas, Despegar/Turismocity, Xotelo API, HotelAPI.
- Sistema de afiliado ético con disclosure transparente.
- `affiliate.config.json` para configurar código de afiliado de Promociones Aéreas.
- README multi-plataforma: Pi, ChatGPT, Claude.

### Cambiado

- Scripts `.py` marcados como opcionales (extra para Pi, no requeridos).
- Skill basada en APIs + `web_search` + `fetch_content` para portabilidad.

## [1.0.1] - 2026-10-07

### Corregido

- Auditoría de publicación: sin secretos, tokens, emails, IPs ni paths
  locales en los archivos (verificado con grep).
- `search_all.py` y `search_flights.py` avisan por stderr cuando falta el
  módulo `browser_helpers` en vez de devolver 0 vuelos en silencio.
- `search_flybondi.py` y `search_all.py` documentan que
  `api.flybondi.com` no resuelve públicamente (verificado 2026-10-07) y que
  `www.flybondi.com` bloquea bots: el script es best-effort con fallback
  manual.
- `SKILL.md` y `README.md` con nota de portabilidad: qué funciona
  standalone (Anduin API, web search) y qué requiere navegador.

## [1.0.0] - 2026-10-07

### Agregado

- Publicación inicial como repo público standalone.
- `SKILL.md` con frontmatter portable (`name`, `description`, `license: MIT`,
  `metadata.author/version`) y sin rutas absolutas hardcodeadas.
- `scripts/` portables (`BROWSER_HELPERS_PATH` con fallback en vez de
  `/opt/data/cache/browser-use`).
- `README.md`, `LICENSE` (MIT), `package.json`, `requirements.txt`,
  `CHANGELOG.md`.
