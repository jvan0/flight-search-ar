# flight-search-ar

Busca vuelos en Argentina (nacionales e internacionales) comparando precios entre
Aerolíneas Argentinas, Flybondi, JetSMART y LATAM.

Combina Google Flights (vía navegador), la API de promos de Anduin
(`https://anduin.ferminrp.com/api/v1/promos`), promociones oficiales de cada
aerolínea, noticias, metabuscadores (Despegar / Turismocity) y comparación de
monedas (ARS / USD / EUR) + promociones bancarias y de billeteras virtuales.

> Esta es la documentación **para humanos**. La instrucción que lee el agente
> está en [`SKILL.md`](./SKILL.md).

## Instalación

### Opción A — skills.sh (recomendada)

```bash
npx skills add jvan0/flight-search-ar
```

El repo público en GitHub es todo lo que se necesita: skills.sh lo indexa por
telemetría de instalación, sin formulario de alta.

### Opción B — clonado manual

```bash
git clone https://github.com/jvan0/flight-search-ar.git
# copiar o linkear a tu carpeta de skills, ej:
ln -s "$(pwd)/flight-search-ar" ~/.agents/skills/flight-search-ar
```

### Opción C — npm / skillpm (opcional)

```bash
npx skillpm install @jvan0/flight-search-ar
```

## Requisitos

- Python 3.10+ y `requests` para los scripts de promos:

```bash
pip install -r requirements.txt
```

### Qué funciona sin navegador (cualquier tercero)

| Fuente | Estado | Cómo |
|---|---|---|
| Anduin Promos API | ✅ Funciona standalone (verificada 2026-10-07: 21 promos) | `python3 scripts/search_all.py --from COR --to AEP --date 2026-11-20 --include-promos` |
| Búsqueda web de promos/noticias | ✅ Con cualquier `web_search` del agente | Ver flujo en `SKILL.md` |
| Flybondi directo | ⚠️ Best-effort (su API no oficial no resuelve públicamente; la web bloquea bots) | `python3 scripts/search_flybondi.py ...` o manual en https://www.flybondi.com/ |
| Google Flights vía scripts | ⚠️ Requiere `browser_helpers` | `export BROWSER_HELPERS_PATH=/ruta/a/tus/browser-helpers` (si falta, el script lo avisa por stderr y sigue) |

- Para las búsquedas vía navegador, los scripts esperan helpers
  (`new_tab`, `wait_for_load`, `js`) resolubles vía `BROWSER_HELPERS_PATH`.
  Si tu harness ya provee automatización de navegador (ej. `browser_exec`),
  seguí el flujo descripto en `SKILL.md` en lugar de los scripts:

```bash
export BROWSER_HELPERS_PATH=/ruta/a/tus/browser-helpers
python3 scripts/search_all.py --help
```

## Estructura

```
flight-search-ar/
├── SKILL.md            # instrucción del agente (único archivo requerido)
├── README.md           # este archivo (humanos)
├── LICENSE            # MIT
├── package.json        # metadata npm/skillpm
├── requirements.txt    # deps Python (requests)
├── scripts/
│   ├── search_all.py       # combina todas las fuentes
│   ├── search_flights.py   # Google Flights vía navegador
│   └── search_flybondi.py  # Flybondi directo
└── CHANGELOG.md
```

## Uso (ejemplos)

```bash
# Ver promos de vuelos (API Anduin)
python3 scripts/search_all.py --promos

# Buscar COR → AEP en una fecha
python3 scripts/search_flights.py --from COR --to AEP --date 2026-11-02

# Buscar directo en Flybondi
python3 scripts/search_flybondi.py --from COR --to AEP --date 2026-11-02
```

Desde el agente, simplemente pedí en lenguaje natural:

> "Buscá vuelos de Córdoba a Buenos Aires para el 29 de octubre, vuelta el 2 de noviembre"

La skill devuelve una tabla comparativa + promociones bancarias aplicables.

## Fuentes de datos

1. Google Flights (vía navegador)
2. API de Anduin (`https://anduin.ferminrp.com/api/v1/promos`, upstream
   `https://promociones-aereas.com.ar`)
3. Sitios y redes oficiales de Aerolíneas / JetSMART / Flybondi
4. Noticias + Despegar / Turismocity
5. Comparación ARS / USD / EUR

## Licencia

MIT — ver [`LICENSE`](./LICENSE).
