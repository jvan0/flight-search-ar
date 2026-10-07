---
name: flight-search-ar
description: "Busca vuelos en Argentina comparando Aerolineas Argentinas, Flybondi, JetSMART y LATAM via Google Flights y API Anduin. Usar cuando pidan vuelos, pasajes u ofertas en Argentina."
license: MIT
metadata:
  author: "jvan0"
  version: "1.0.0"
---

# Flight Search Argentina

Busca vuelos en Argentina comparando precios entre múltiples aerolíneas y fuentes.

## Fuentes de datos

1. **Google Flights** — vía navegador (cubre Aerolíneas Argentinas, JetSMART, Flybondi, LATAM)
2. **Anduin Promos API** — promociones de vuelos nacionales e internacionales (https://anduin.ferminrp.com/api/v1/promos)
3. **Promociones oficiales** — redes sociales y sitios oficiales de aerolíneas
4. **Noticias** — búsqueda de noticias sobre aerolíneas argentinas
5. **Despegar / Turismocity** — metabuscadores con ofertas exclusivas
6. **Comparación de monedas** — ARS vs USD vs EUR para detectar diferencias de precio

## Tipos de búsqueda

### Vuelos nacionales (cabotaje)
- Usar Google Flights + Anduin Promos + promociones oficiales
- Aerolíneas: Aerolíneas Argentinas, JetSMART, Flybondi, LATAM

### Vuelos internacionales
- Usar Anduin Promos API (skill de ferminrp) + Google Flights
- La API de Anduin cubre promos de vuelos internacionales desde Argentina
- Fuente upstream: https://promociones-aereas.com.ar
- Canal de novedades: https://t.me/comparaviajes

## Flujo de búsqueda

### 1. Búsqueda en Google Flights

Usar `browser_exec` para navegar a Google Flights:

```python
# Construir URL
from_airport = "COR"  # Córdoba
to_airport = "AEP"    # Buenos Aires (Aeroparque)
date = "2026-10-29"
return_date = "2026-11-02"  # opcional

url = f"https://www.google.com/travel/flights?q=Flights+from+{from_airport}+to+{to_airport}+on={date}+one+way&hl=es&curr=ARS"
if return_date:
    url += f"+returning+{return_date}"

# Navegar y extraer resultados
new_tab(url)
wait_for_load()
time.sleep(3)

results = js("""
(() => {
  const text = document.body.innerText;
  const idx = text.indexOf('Resultados de búsqueda');
  if (idx >= 0) return text.substring(idx, idx + 10000);
  return text.substring(0, 10000);
})()
""")
```

### 2. Búsqueda en Flybondi

Flybondi no tiene API pública. Buscar directamente en su sitio web:

```python
url = f"https://www.flybondi.com/compra-vuelos?from={from_airport}&to={to_airport}&date={date}&adults=1&tripType=oneWay"
new_tab(url)
wait_for_load()
time.sleep(5)
```

### 3. Búsqueda en Anduin Promos (nacionales e internacionales)

La API de Anduin cubre promos de vuelos nacionales e internacionales desde Argentina.
Fuente upstream: https://promociones-aereas.com.ar
Canal de novedades: https://t.me/comparaviajes

```bash
# Buscar todas las promos de vuelos
curl -s "https://anduin.ferminrp.com/api/v1/promos" | python3 -c "
import json, sys
data = json.load(sys.stdin)
promos = data.get('data', {}).get('promos', [])
vuelos = [p for p in promos if p.get('category') == 'vuelos']
for p in vuelos:
    print(f\"{p['title']} | {p.get('destinationCountry')} | Score: {p.get('score')}\")
    print(f\"  Link: {p['permalink']}\")
"

# Filtrar por país destino
curl -s "https://anduin.ferminrp.com/api/v1/promos" | python3 -c "
import json, sys
data = json.load(sys.stdin)
promos = data.get('data', {}).get('promos', [])
vuelos = [p for p in promos if p.get('category') == 'vuelos' and p.get('destinationCountry') == 'brazil']
for p in vuelos:
    print(f\"{p['title']} | Score: {p.get('score')}\")
    print(f\"  Link: {p['permalink']}\")
"
```

### 4. Búsqueda de promociones oficiales

Buscar en las fuentes oficiales de cada aerolínea:

#### Aerolíneas Argentinas
- Web: https://www.aerolineas.com.ar/promociones
- Twitter/X: https://x.com/AerolineasARG
- Instagram: https://www.instagram.com/aerolineasarg

#### JetSMART
- Web: https://www.jetsmart.com/ar/promociones
- Twitter/X: https://x.com/JetSmartAR
- Instagram: https://www.instagram.com/jetsmartar

#### Flybondi
- Web: https://www.flybondi.com/promociones
- Twitter/X: https://x.com/flybondi
- Instagram: https://www.instagram.com/flybondi

### 5. Búsqueda de noticias

Usar `web_search` para buscar noticias recientes:

```python
# Noticias sobre aerolíneas argentinas
web_search("Aerolíneas Argentinas promociones ofertas 2026")
web_search("JetSMART Argentina promociones ofertas 2026")
web_search("Flybondi Argentina promociones ofertas 2026")
web_search("vuelos baratos Argentina 2026")
```

### 5. Búsqueda en Despegar / Turismocity

Estos metabuscadores a veces tienen ofertas exclusivas que no están en Google Flights:

```python
# Despegar
url = f"https://www.despegar.com.ar/vuelos/{from_airport}/{to_airport}/{date}"
new_tab(url)
wait_for_load()
time.sleep(5)

# Turismocity
url = f"https://www.turismocity.com.ar/vuelos/{from_airport}/{to_airport}/{date}"
new_tab(url)
wait_for_load()
time.sleep(5)
```

### 6. Comparación de monedas

Google Flights puede mostrar precios diferentes según la moneda seleccionada. Probar en ARS, USD y EUR:

```python
# ARS (por defecto)
url_ars = f"https://www.google.com/travel/flights?q=Flights+from+{from_airport}+to+{to_airport}+on={date}+one+way&hl=es&curr=ARS"

# USD
url_usd = f"https://www.google.com/travel/flights?q=Flights+from+{from_airport}+to+{to_airport}+on={date}+one+way&hl=en&curr=USD"

# EUR
url_eur = f"https://www.google.com/travel/flights?q=Flights+from+{from_airport}+to+{to_airport}+on={date}+one+way&hl=es&curr=EUR"
```

Comparar los precios y mostrar la opción más barata. A veces el precio en USD es más bajo que en ARS por diferencias de tipo de cambio.

## Códigos de aeropuertos

| Ciudad | Código | Aeropuerto |
|--------|--------|------------|
| Córdoba | COR | Ingeniero Ambrosio Taravella |
| Buenos Aires | AEP | Aeroparque Jorge Newbery |
| Buenos Aires | EZE | Ministro Pistarini (Ezeiza) |
| Mendoza | MDZ | Francisco Gabrielli |
| Bariloche | BRC | San Carlos de Bariloche |
| Salta | SLA | Martín Miguel de Güemes |
| Rosario | ROS | Rosario – Islas Malvinas |
| Tucumán | TUC | Benjamín Matienzo |
| Neuquén | NQN | Presidente Perón |
| Iguazú | IGR | Cataratas del Iguazú |

## Formato de salida

La skill devuelve una tabla comparativa:

```
| Hora | Aerolínea | Ruta | Duración | Precio | Fuente |
|------|-----------|------|----------|--------|--------|
| 22:00 → 23:18 | JetSMART | COR–AEP | 1h 18min | 30.493 ARS | Google Flights |
| 11:50 → 13:10 | Aerolíneas Argentinas | COR–EZE | 1h 20min | 60.147 ARS | Google Flights |
```

## Promociones bancarias y billeteras virtuales

En Argentina, los bancos y billeteras virtuales tienen promociones fuertes con aerolíneas.
La skill debe buscar estas promociones para maximizar el ahorro.

### Fuentes oficiales de promociones bancarias

#### Aerolíneas Argentinas
- Promociones vigentes: https://www.aerolineas.com.ar/vuelos-por-argentina
- Bancos con cuotas sin interés: Banco Nación, Galicia, Macro, Patagonia, ICBC, Santander, BBVA, American Express, Naranja X, Credicoop, Cabal, Banco Ciudad, Banco San Juan
- Ejemplo: "3 y 6 cuotas sin interés con Banco Nación", "18 cuotas con Patagonia 365"

#### JetSMART
- Promociones vigentes: https://jetsmart.com/ar/es/minisitios/legales
- Medios de pago: https://jetsmart.com/ar/es/minisitios/medios-de-pago
- Ejemplo: "20% descuento con Banco del Chubut", "30% OFF con Mastercard"

#### Flybondi
- Promociones vigentes: https://flybondi.com/ar/promociones
- Ejemplo: "3 cuotas sin interés con Banco Columbia", "20% reintegro con tarjeta Flybondi"

### Billeteras virtuales

| Billetera | Promociones con aerolíneas | Fuente |
|-----------|---------------------------|--------|
| **Mercado Pago** | Buscar en https://www.mercadopago.com.ar/ayuda | Ayuda oficial |
| **Ualá** | Buscar en https://www.uala.com.ar/ayuda | Ayuda oficial |
| **Brubank** | Buscar en https://www.brubank.com.ar/ayuda | Ayuda oficial |
| **Naranja X** | Buscar en https://naranjax.com/ayuda | Ayuda oficial |
| **Personal Pay** | Buscar en https://www.personalpay.com.ar/ayuda | Ayuda oficial |
| **Cocos** | Buscar en https://www.cocos.capital/ayuda | Ayuda oficial |
| **Belo** | Buscar en https://www.belo.app/ayuda | Ayuda oficial |

### Cómo buscar promociones bancarias

```python
# Buscar promociones vigentes de Aerolíneas Argentinas
web_search("Aerolíneas Argentinas cuotas sin interés bancos 2026")

# Buscar promociones vigentes de JetSMART
web_search("JetSMART cuotas sin interés bancos 2026")

# Buscar promociones vigentes de Flybondi
web_search("Flybondi cuotas sin interés bancos 2026")

# Buscar promociones de billeteras virtuales
web_search("Mercado Pago Ualá Brubank descuento vuelos aerolíneas 2026")
```

### Formato de salida para promociones bancarias

```
| Aerolínea | Banco/Billetera | Descuento | Cuotas | Vigencia | Fuente |
|-----------|-----------------|-----------|--------|----------|--------|
| Aerolíneas Argentinas | Banco Nación | - | 3/6 CSI | 24/09-04/10/2026 | aerolineas.com.ar |
| Aerolíneas Argentinas | Patagonia 365 | - | 3/6/9/12/18 CSI | 01/08-30/09/2026 | aerolineas.com.ar |
| JetSMART | Banco del Chubut | 20% | 12 CSI | 29/08-31/12/2026 | jetsmart.com |
| Flybondi | Banco Columbia | - | 3 CSI | 01/01-31/07/2026 | flybondi.com |
```

## Integración con travel-promos-argentina (ferminrp)

La skill `travel-promos-argentina` (misma fuente: API de Anduin, https://anduin.ferminrp.com/api/v1/promos)
es la fuente principal para vuelos internacionales. Esta skill la integra automáticamente.

### Cómo funciona la integración

1. **Vuelos internacionales:** La skill consulta la API de Anduin (misma fuente que travel-promos-argentina)
2. **Vuelos nacionales:** Además consulta Google Flights y promociones oficiales
3. **Promos especiales:** La API de Anduin puede tener promos que no están en Google Flights

### Diferencias entre las skills

| Aspecto | flight-search-ar | travel-promos-argentina |
|---------|------------------|------------------------|
| Vuelos nacionales | ✅ Google Flights + Anduin | ❌ Solo Anduin |
| Vuelos internacionales | ✅ Anduin + Google Flights | ✅ Anduin |
| Promociones oficiales | ✅ Redes sociales + web | ❌ Solo Anduin |
| Noticias | ✅ Búsqueda de noticias | ❌ No |
| Comparación de monedas | ✅ ARS/USD/EUR | ❌ No |
| Metabuscadores | ✅ Despegar/Turismocity | ❌ No |

### Cuándo usar cada skill

- **flight-search-ar:** Cuando el usuario quiere comparar precios entre aerolíneas y fuentes
- **travel-promos-argentina:** Cuando el usuario quiere ver promos internacionales específicamente

## Notas

- Los precios de Google Flights **incluyen impuestos y tasas** (verificado en la página)
- Los precios **NO incluyen equipaje facturado** en JetSMART y Flybondi
- Aerolíneas Argentinas incluye equipaje despachado
- Los precios son para 1 adulto en clase turista
- La API de Anduin puede tener promos que no están en Google Flights
- Para vuelos de ida y vuelta, buscar por separado (ida y vuelta) para obtener mejores precios
- Flybondi bloquea acceso automatizado (Cloudflare) — buscar manualmente en su sitio web
- **El navegador ya es anónimo por defecto** — no hay cookies persistentes ni historial entre sesiones
- **No se usa VPN** — no es necesaria para vuelos domésticos argentinos y añade complejidad sin garantía de mejores precios
- **Comparar monedas** (ARS vs USD vs EUR) puede revelar diferencias de precio por tipo de cambio
- **Despegar y Turismocity** a veces tienen ofertas exclusivas que no están en Google Flights
- **Integración con travel-promos-argentina:** Esta skill usa la misma API de Anduin que la skill de ferminrp, por lo que las promos internacionales están cubiertas
- **Promociones bancarias:** Los bancos argentinos ofrecen cuotas sin interés y descuentos con aerolíneas. Buscar siempre en las fuentes oficiales de cada aerolínea
- **Billeteras virtuales:** Mercado Pago, Ualá, Brubank, Naranja X, Personal Pay, Cocos y Belo pueden tener promociones exclusivas con aerolíneas

## Ejemplo de uso

### Vuelos nacionales
Usuario: "Buscá vuelos de Córdoba a Buenos Aires para el 29 de octubre, vuelta el 2 de noviembre"

1. Buscar en Google Flights: COR → AEP, 2026-10-29 (en ARS, USD y EUR)
2. Buscar en Google Flights: AEP → COR, 2026-11-02 (en ARS, USD y EUR)
3. Buscar en Anduin Promos
4. Buscar promociones oficiales en redes sociales de aerolíneas
5. Buscar noticias sobre ofertas y promociones
6. Buscar en Despegar y Turismocity
7. Buscar promociones bancarias (cuotas sin interés, descuentos por banco/tarjeta)
8. Buscar promociones de billeteras virtuales (Mercado Pago, Ualá, Brubank, Cocos, Belo, etc.)
9. Comparar precios y mostrar tabla con la opción más barata + promociones bancarias aplicables

### Vuelos internacionales
Usuario: "Buscá vuelos de Córdoba a Brasil"

1. Buscar en Anduin Promos API (filtrar por destinationCountry == "brazil")
2. Buscar en Google Flights: COR → GRU/GIG, fechas flexibles
3. Buscar promociones oficiales en redes sociales de aerolíneas
4. Buscar noticias sobre ofertas y promociones
5. Mostrar tabla con promos y precios comparados
