# SERCOP Procurement Portal – Discovery Notes

_Last updated: 2025-03-??_

## Scope

These notes capture the current understanding of the public procurement search portal operated by SERCOP (`compraspublicas.gob.ec`). They focus on the HTML structure, JavaScript workflow, network endpoints, and constraints that impact programmatic harvesting. They are meant to guide the implementation of `real_sercop_scraper.py` and any future ingestion automation.

## Entry point & session bootstrap

- **Search page URL:** `https://www.compraspublicas.gob.ec/ProcesoContratacion/compras/PC/buscarProceso.cpe?sg=1`
- The first `GET` call establishes a PHP session (`PHPSESSID`) and returns a Base64-encoded `csrf_token` hidden field that must be echoed on every POST.
- The response also embeds the procurement search form (`<form id="frmDatos">`) with numerous hidden controls used by the synchronous Prototype.js workflow.
- A captcha image is embedded immediately: `../exe/generadorCaptcha.php`. The same session cookie must be used when downloading the captcha and when submitting the search.

### Required cookies & headers

The in-browser flow sets the following request headers:

- `X-Requested-With: XMLHttpRequest`
- `X-Prototype-Version: 1.7`
- `Content-Type: application/x-www-form-urlencoded; charset=UTF-8`
- `Referer: https://www.compraspublicas.gob.ec/ProcesoContratacion/compras/buscarProceso.cpe`

Prototype.js handles these automatically; a Python client must add them explicitly when calling AJAX endpoints.

## Search form anatomy

Key controls rendered inside `frmDatos`:

| Field name | Type | Default | Notes |
|------------|------|---------|-------|
| `csrf_token` | hidden | Base64 string | Must be echoed unchanged.
| `captccc2` | hidden | `1` | Toggles captcha validations (set to `1` before the first AJAX call, `2` on subsequent pagination requests).
| `txtPalabrasClaves` | text | `` | Free-text keyword search.
| `Entidadbuscar` | hidden | `` | Internal entity identifier produced by the "Buscar Entidad" popup.
| `cmbEntidad` | hidden | `` | Receives the selected entity code from the popup.
| `txtEntidadContratante` | textarea | `` | Human-readable entity name; the code is what the backend consumes.
| `txtCodigoTipoCompra` | select | `""` | Type of contracting process (Licitación, Subasta inversa, etc.). Selecting a value triggers additional AJAX combos for state & type.
| `cmbTipoCompra` | select (dynamic) | absent | Populated via `TcomTipoProceso.TipoCompra`; only present for specific contracting types.
| `cmbEstado` | select (dynamic) | absent | Populated via `ManejadorCatalogo.arregloCatalogoEstados`, depends on contracting type.
| `txtCodigoProceso` | text | `` | Exact procurement code filter.
| `f_inicio` / `f_fin` | text (readonly) | Today ± 6 months window | Publication date range. Calendar widget constrains to 6 months back + 15 days forward.
| `image` | text | `` | User-entered captcha text (required).
| `count` | hidden | `` | Populated after `buscarProcesoxEntidadCount` returns.
| `paginaActual` | hidden | `` | Zero-based offset (multiples of 20).
| `estado` | hidden | `` | Primarily used by internal workflows; left blank for public searches.
| `trx` | hidden | `` | Blank in public context.

Supporting UX elements:

- `btnBuscarEntidad` opens `buscarEntidad.cpe?op=1` in a popup to select contracting entities.
- "Reload Captcha" button calls `reloadCaptcha()` (defined in their bundled scripts) to refresh the image via `generadorCaptcha.php`.

## AJAX search workflow

When the user clicks **Buscar**, Prototype.js executes the following sequence (see `rag/tmp/buscarProceso.js` for reference):

1. Validate dates (≤ 6-month window) and ensure captcha is filled.
2. `captccc2` is forced to `1` and `paginaActual` to `0`.
3. Call `SolicitudCompra.buscarProcesoxEntidadCount` to obtain the total result count.
   - POST target: `https://www.compraspublicas.gob.ec/ProcesoContratacion/servicio/interfazWeb.php`
   - Payload: `__class=SolicitudCompra&__action=buscarProcesoxEntidadCount&` + serialized form data (URL-encoded)
   - Response: JSON object `{ "count": <int> }`
4. If a non-zero count is returned, call `SolicitudCompra.buscarProcesoxEntidad` to retrieve the first page.
   - Same endpoint and payload pattern, but with `__action=buscarProcesoxEntidad`.
   - `registroxPagina` is hard-coded at 20 rows; `paginaActual` is the offset (0, 20, 40...).
   - After the first load, the frontend sets `captccc2=2` and reuses the same call for pagination.
5. A subsequent `linkReload.click()` forces a new captcha render after each successful fetch.

### Sample request skeleton

```text
POST /ProcesoContratacion/servicio/interfazWeb.php HTTP/1.1
Host: www.compraspublicas.gob.ec
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
X-Requested-With: XMLHttpRequest
X-Prototype-Version: 1.7
Cookie: PHPSESSID=…; other portal cookies

__class=SolicitudCompra&__action=buscarProcesoxEntidad&csrf_token=<TOKEN>&captccc2=1&txtPalabrasClaves=computador&Entidadbuscar=...&cmbEntidad=...&txtCodigoTipoCompra=387&...&image=<CAPTCHA>&paginaActual=0&count=&
```

All form fields (even empty ones) are serialized. Omitting the captcha or using the wrong value produces either `result === "fallo"` (rendered as "Captcha Incorrecto") or a redirect script to `index.php?swin=<code>&err=2`.

## Response structure

`SolicitudCompra.buscarProcesoxEntidad` returns JSON parsed by Prototype and exposed to `listarProcesos(result, resp)` where `result` is an array of records. Each record exposes concise keys consumed by the UI:

| Key | Meaning (inferred) | Notes |
|-----|--------------------|-------|
| `c` | Process code | Displayed as the primary link.
| `i` | Internal `idSoliCompra` | Used to build detail URLs (`informacionProcesoContratacion.cpe?idSoliCompra=…`).
| `v` | Version flag | `2` opens modal view, `3` for ferias inclusivas, `-1/-2` legacy routes.
| `r` | Contracting entity name | Second column.
| `d` | Object / description | Third column.
| `g` | Process state | E.g. `Adjudicada`, `Borrador`.
| `j` | Purchase type | Only populated when `muestraTipoCompra === 'SI'`.
| `s` | Province/Cantón | Geographic metadata.
| `t` | Numeric type discriminator | Controls how budget is shown (e.g., 4505 → "No aplica").
| `p` | Referential budget | Rendered with 2 or 4 decimals depending on `t`.
| `f` | Publication or creation date | Column labelled "Fecha de Publicación" or "Fecha de Creación".
| `z` | Alternate date | Used when `g === 'Borrador'` to decide display date.
| `e` | Option flag | When `modFecha`, an extra "Cambio de Cronograma" link is rendered.
| `u` | Hidden date string | Used for internal financing logic.

Each page returns up to 20 records. Pagination uses `paginaActual` offsets and the total count in `count` to render navigation links (Inicio, Anterior, Siguiente, Fin).

### Detail pages

Row links land on one of the following, depending on the `v` flag:

- `informacionProcesoContratacion.cpe?idSoliCompra=<ID>` – standard detail view.
- `informacionProcesoContratacion2.cpe?idSoliCompra=<ID>` – modal variant.
- `../SC/sci.cpe?idSoliCompra=<ID>` – legacy pipeline for drafts.

Each detail page exposes tabs for documents, adjudication data, and milestone history; these require additional HTML parsing per process.

## Captcha enforcement

- The text input `image` must match the distorted characters served by `generadorCaptcha.php` for the active session.
- The captcha is refreshed immediately after a successful `listarProcesos` call via the hidden `linkReload` anchor.
- Failed captcha attempts (`result === "fallo"`) leave the captcha in place but require a manual refresh to continue.
- Programmatic scraping therefore **must** solve or bypass the captcha for every request cycle. Options:
  1. **Human-in-the-loop:** Cache the captcha image to S3 and request manual entry via an internal tool (feasible for small batches or bootstrapping).
  2. **OCR + heuristics:** Use `pytesseract` with aggressive preprocessing. Early tests (not committed) suggest moderate noise; expect ~60–70% accuracy without custom training.
  3. **External solving service:** Integrate a service such as 2Captcha / Anti-Captcha. Requires latency buffering (~15–20 s) but yields deterministic success.
  4. **SERCOP API alternative:** Investigate whether SERCOP exposes open data (OCDS JSON) or a SOAP service that omits captcha. No such endpoint was found during this reconnaissance.

Without captcha resolution the server responds with the login HTML (`index.php?swin=…&err=2`), even when the rest of the payload mirrors browser requests. This is the current blocker for automation.

## Additional UI-driven endpoints

The search page dynamically queries auxiliary endpoints via the same `interfazWeb.php` controller:

| Action | Purpose | Notes |
|--------|---------|-------|
| `TcomTipoProceso.TipoCompra` | Populate the `cmbTipoCompra` combo when contracting type supports sub-categories. | Returns array `[{ id, tipo }]`.
| `ManejadorCatalogo.arregloCatalogoEstados` | Provide available states per contracting type. | Feeds the `cmbEstado` select.
| `Parametro.buscarValorParametroSIE` | Several UX toggles (e.g., enabling cronogram changes). | Not required for data fetching.
| `SolicitudCompra.buscarProcesoxEntidadCount` | Result count. | Needs captcha.
| `SolicitudCompra.buscarProcesoxEntidad` | Page results. | Needs captcha.

The "Buscar Entidad" popup (`buscarEntidad.cpe?op=1`) allows users to pick contracting entities; it in turn calls backend services to resolve the selected entity code (`Entidadbuscar` + `cmbEntidad`) which must be included in the main form submission to filter by entity.

## Automation strategy

1. **Session bootstrap:** Instantiate a `requests.Session`, GET the search page, persist cookies, scrape `csrf_token`, and detect any additional hidden inputs.
2. **Captcha fetch & solving:** Download `../exe/generadorCaptcha.php` within the same session. Route the image through the chosen solving strategy; keep the textual answer handy for immediate submission (captcha expires quickly).
3. **Prepare payload:** Build a dict mirroring `Form.serialize(frmDatos)`. Always include every field, even when blank. Set `paginaActual=0`, `captccc2=1`, `count=0`.
4. **Count call:** POST to `servicio/interfazWeb.php` with `__class=SolicitudCompra` and `__action=buscarProcesoxEntidadCount`. Validate the captcha; if the response is HTML instead of JSON, refresh the captcha and retry.
5. **Listing call:** On success, POST again with `__action=buscarProcesoxEntidad`. Store both the parsed JSON and the raw text for audit.
6. **Pagination:** For offsets > 0 set `paginaActual` to the next multiple of 20 and `captccc2=2`, then repeat the listing call. The captcha must be refreshed each time.
7. **Detail harvesting:** For each returned record, request the appropriate detail URL. These pages do not re-check the captcha but do rely on the same session cookie.
8. **Resilience:** Implement exponential backoff on HTTP 30x → login redirects (signalling captcha expiry) and maintain a capped retry queue to avoid account blocking.

### Human-in-the-loop captcha queue

When automated solving is not available, you can stage captcha jobs for manual entry:

- Run `rag/ingest/sercop_captcha_queue.py` with `--batch-size` set to the number of captchas a human can solve immediately (they expire within minutes).
- The script writes captcha images under `rag/ingest/comprehensive_data/sercop_captcha_queue/captchas/` and appends metadata to `manifest.jsonl` containing the session cookies, default form payload, and a relative path to the image.
- Share the `captchas/` folder (or an archive) plus the manifest with the human solver. They should transcribe the captcha text into a new field, e.g. `solution`, per manifest entry.
- Feed the enriched manifest back into the ingestion pipeline, hydrating each queued task with the solved captcha before calling `buscarProcesoxEntidadCount`/`buscarProcesoxEntidad`.

Because the portal refreshes the captcha after every successful query, collect only the number of tasks you can consume in real time; stale entries will return login redirects and must be discarded.

## Open questions & next steps

- **Captcha solving integration** – choose and implement the preferred approach (likely an external service with audit logging).
- **Entity dictionary** – decide whether to pre-load entity codes via the popup’s backend service to avoid manual selection.
- **Historical depth** – the UI limits publication date ranges to 6 months back. Confirm whether pagination across date windows permits full-history coverage or if an authenticated channel is required.
- **Document downloads** – detail views expose attachments hosted under `/ProcesoContratacion/archivos/`. Plan for fetching and deduplicating these per process.
- **Rate limits** – instrument the scraper with throttling (Prototype defaults are synchronous; mimic human pacing to avoid IP bans).

Once captcha handling is solved, implementation can proceed following the skeleton above. A good first milestone is a command-line prototype that pulls counts and the first page for a fixed entity + date range, stores the JSON payloads, and evaluates captcha solving accuracy.
