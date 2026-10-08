# travel-search-ar

Busca vuelos y hoteles en Argentina comparando precios entre múltiples fuentes:
Aerolíneas Argentinas, Flybondi, JetSMART, LATAM, Google Flights, Google Hotels,
API de Anduin, Promociones Aéreas, Despegar, Turismocity, Xotelo y HotelAPI.

> **Instalación para usuarios sin experiencia en IA:**
> Solo decile a tu agente que instale:
> **https://github.com/jvan0/travel-search-ar**

Esta es la documentación **para humanos**. La instrucción que lee el agente
está en [`SKILL.md`](./SKILL.md).

## Instalación

### Opción A — skills.sh (recomendada)

```bash
npx skills add jvan0/travel-search-ar
```

El repo público en GitHub es todo lo que se necesita: skills.sh lo indexa por
telemetría de instalación, sin formulario de alta.

### Opción B — clonado manual

```bash
git clone https://github.com/jvan0/travel-search-ar.git
# copiar o linkear a tu carpeta de skills, ej:
ln -s "$(pwd)/travel-search-ar" ~/.agents/skills/travel-search-ar
```

### Opción C — npm / skillpm (opcional)

```bash
npx skillpm install @jvan0/travel-search-ar
```

## Uso en diferentes plataformas

### Pi (esta skill)

La skill se instala en `~/.pi/agent/skills/travel-search-ar/` y se activa
automáticamente cuando el usuario pide vuelos u hoteles.

### ChatGPT (Custom GPT)

1. Crear un Custom GPT en https://chatgpt.com/gpts/editor
2. En "Instructions", pegar el contenido de `SKILL.md`
3. En "Knowledge", subir el archivo `SKILL.md`
4. El Custom GPT ahora puede buscar vuelos y hoteles

### Claude.ai (Project)

1. Crear un Project en https://claude.ai/projects
2. En "Project Instructions", pegar el contenido de `SKILL.md`
3. Subir `SKILL.md` como knowledge file
4. El proyecto ahora puede buscar vuelos y hoteles

### Claude Code

```bash
git clone https://github.com/jvan0/travel-search-ar.git
# copiar a tu carpeta de skills de Claude Code
```

## Requisitos

- Python 3.10+ y `requests` para los scripts de promos (opcional):

```bash
pip install -r requirements.txt
```

### Qué funciona sin navegador (cualquier agente)

| Fuente | Estado | Cómo |
|---|---|---|
| Anduin Promos API (vuelos + hoteles) | ✅ Funciona standalone | `curl` o `fetch_content` |
| Búsqueda web de promos/noticias | ✅ Con `web_search` del agente | Ver flujo en `SKILL.md` |
| Xotelo API (hoteles) | ✅ API gratuita | `curl` o `fetch_content` |
| HotelAPI / makcorps (hoteles) | ✅ API gratuita | `curl` o `fetch_content` |
| Google Flights/Hotels | ⚠️ Requiere navegador | `browser_exec` o manual |
| Flybondi directo | ⚠️ Best-effort | Web manual |

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
travel-search-ar/
├── SKILL.md              # instrucción del agente (único archivo requerido)
├── README.md             # este archivo (humanos)
├── LICENSE              # MIT
├── package.json         # metadata npm/skillpm
├── requirements.txt     # deps Python (requests)
├── affiliate.config.json # config de afiliado (opcional)
├── scripts/
│   ├── search_all.py       # combina todas las fuentes (opcional)
│   ├── search_flights.py   # Google Flights vía navegador (opcional)
│   └── search_flybondi.py  # Flybondi directo (opcional)
└── CHANGELOG.md
```

## Uso (ejemplos)

```bash
# Ver promos de vuelos y hoteles (API Anduin)
python3 scripts/search_all.py --promos

# Buscar COR → AEP en una fecha
python3 scripts/search_flights.py --from COR --to AEP --date 2026-11-02

# Buscar directo en Flybondi
python3 scripts/search_flybondi.py --from COR --to AEP --date 2026-11-02
```

Desde el agente, simplemente pedí en lenguaje natural:

> "Buscá vuelos de Córdoba a Buenos Aires para el 29 de octubre, vuelta el 2 de noviembre"

> "Buscá hoteles en Bariloche del 15 al 20 de diciembre"

La skill devuelve una tabla comparativa + promociones bancarias aplicables.

## Fuentes de datos

### Vuelos
1. Google Flights (vía navegador)
2. API de Anduin (`https://anduin.ferminrp.com/api/v1/promos`, upstream
   `https://promociones-aereas.com.ar`)
3. Sitios y redes oficiales de Aerolíneas / JetSMART / Flybondi
4. Noticias + Despegar / Turismocity
5. Comparación ARS / USD / EUR

### Hoteles
1. Google Hotels (vía navegador)
2. API de Anduin (categoría `hoteles`)
3. Promociones Aéreas (sección hoteles)
4. Despegar / Turismocity
5. Xotelo API (gratuita)
6. HotelAPI / makcorps (gratuita)

## Afiliado ético

Esta skill puede incluir códigos de referido en links de Promociones Aéreas.
**Siempre** se muestra el disclosure:

> Puede contener código de referido, esto me ayuda a seguir creando herramientas gratuitas :)

Para activar: editar `affiliate.config.json` con tu código de afiliado.
Registrarse en https://promociones-aereas.com.ar/afiliados (gratis).

## Licencia

MIT — ver [`LICENSE`](./LICENSE).
