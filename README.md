# Dashboard de Incidencia Delictiva en México

Dashboard interactivo construido con Streamlit que integra dos bases del SESNSP:

- **Fuero común** (incidencia municipal, 2015–2019) — `IDM_NM_dic25.csv`
- **Fuero federal** (2012–2026) — `Fuero_federal_2012-2026_abr2026.csv`

Incluye filtros dinámicos (año, entidad), KPIs, gráficas interactivas (Plotly) y descarga de datos filtrados.

---

## Archivos del proyecto

```
streamlit_app.py                       ← la aplicación
requirements.txt                       ← dependencias
IDM_NM_dic25.csv.gz                    ← datos del fuero común (comprimido)
Fuero_federal_2012-2026_abr2026.csv    ← datos del fuero federal
```

**Importante:** los cuatro archivos deben estar en la MISMA carpeta (la raíz del repositorio).

> El archivo del fuero común se entrega **comprimido (`.csv.gz`, 5.7 MB)** porque el original pesa ~147 MB y supera el límite de subida web de GitHub (25 MB). La compresión no pierde ningún dato: pandas lee el `.gz` directamente y la app ya está configurada para ello. **Sube el `.gz` tal cual, no lo descomprimas.**

---

## Paso a paso para desplegar GRATIS en Streamlit Community Cloud

### 1. Crear una cuenta de GitHub (si no tienes)
Ve a https://github.com y regístrate. Es gratis.

### 2. Crear un repositorio nuevo
- Clic en **New repository**.
- Nombre, por ejemplo: `dashboard-seguridad-mexico`.
- Marca **Public** (Community Cloud requiere repos públicos para apps públicas gratuitas).
- Clic en **Create repository**.

### 3. Subir los cuatro archivos
- En el repositorio, clic en **Add file → Upload files**.
- Arrastra `streamlit_app.py`, `requirements.txt`, `IDM_NM_dic25.csv.gz` y `Fuero_federal_2012-2026_abr2026.csv`.
- Clic en **Commit changes**.

> El `.csv.gz` ya está por debajo del límite de GitHub. Súbelo comprimido, sin descomprimir.

### 4. Conectar Streamlit Community Cloud
- Ve a https://share.streamlit.io
- Inicia sesión con tu cuenta de GitHub y autoriza el acceso.

### 5. Desplegar la app
- Clic en **Create app** (o **New app**).
- Selecciona:
  - **Repository:** `tu-usuario/dashboard-seguridad-mexico`
  - **Branch:** `main`
  - **Main file path:** `streamlit_app.py`
- Clic en **Deploy**.
- Espera 2–5 minutos mientras instala dependencias y arranca.

Tu app quedará en una URL como:
```
https://dashboard-seguridad-mexico.streamlit.app
```

### 6. Hacerla pública
- Dentro de la app, esquina superior derecha: **Share**.
- En **Sharing**, selecciona **"This app is public and searchable"**.
- Copia la URL. Cualquiera con el enlace podrá verla.

---

## Cómo embeberla en tu sitio web (iframe)

Para incrustarla en tu página (por ejemplo, en la sección de Dashboard Municipal de tu sitio), añade `?embed=true` al final de la URL:

```html
<iframe
  src="https://dashboard-seguridad-mexico.streamlit.app/?embed=true"
  width="100%"
  height="900px"
  frameborder="0">
</iframe>
```

El parámetro `?embed=true` oculta el menú y el encabezado de Streamlit para que se vea limpio dentro de tu página.

**Recomendación:** prueba el iframe en Chrome, Safari y móvil. Si en algún navegador no carga (limitación conocida de Streamlit en ciertos iframes), tienes como respaldo la versión HTML estática o Looker Studio.

---

## Probar en local (opcional)

Si quieres verlo en tu computadora antes de desplegar:

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Se abrirá en `http://localhost:8501`.

---

## Notas sobre los datos

- Las cifras son **presuntos delitos registrados** (carpetas de investigación), no víctimas ni sentencias.
- No incluyen la **cifra negra** (delitos no denunciados).
- El año **2026 del fuero federal es parcial** (enero–abril); por defecto se excluye de las series de tendencia.
- Las cifras absolutas **no están normalizadas por población**.

**Fuente primaria:** Secretariado Ejecutivo del Sistema Nacional de Seguridad Pública (SESNSP).
