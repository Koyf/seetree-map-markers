# Map Markers

Take-home for SeeTree. A single-page app on Mapbox GL JS where the user places
markers with a score 0–5, edits, moves and removes them, sees per-score counts,
and exports/imports them as JSON. A FastAPI server owns the markers and randomly
refuses to create one, so the client has to handle failure.

Full behaviour and API contract: [SPEC.md](SPEC.md).

Live: https://markers-client-fmeovlq6fq-ew.a.run.app (API: https://markers-server-fmeovlq6fq-ew.a.run.app/docs).

## Run

Docker, one command:

```bash
cp .env.example .env      # paste the Mapbox token from the task
docker compose up --build
```

Client: http://localhost:5173, API + Swagger: http://localhost:8000/docs.
Markers are kept in `./data/markers.json` on the host and survive restarts.

Without Docker (Python 3.14 + [uv](https://docs.astral.sh/uv/), Node 22):

```bash
cd server && uv sync && uv run uvicorn app.main:app --reload   # :8000
cd client && npm ci && npm run dev                              # :5173
```

Checks:

```bash
cd server && uv run ruff check . && uv run pytest -q
cd client && npx tsc --noEmit && npm run build
```

## Architecture

```
client/src/                      server/app/
  main.ts       boot: toolbar, map click, initial load      main.py     FastAPI app + CORS
  markers.ts    marker state + create/score/move/remove     routes.py   6 endpoints under /markers
  popup.ts      the one open popup                          storage.py  MarkerStore: one JSON file + lock
  scoreButtons  0..5 colored buttons                        failure.py  should_fail(): random 1/3
  importFile.ts JSON file -> POST /markers/import           models.py   Pydantic: MarkerIn, Marker, ...
  toolbar.ts    Export / Import / Clear all
  api.ts        fetch wrapper, one Error per failure
  stats.ts      top-right panel      toast.ts  messages     types.ts  Marker, Score, colors
```

- The server is the source of truth: every change is a request, the client draws
  only what the server confirmed, and a page reload restores state from `GET /markers`.
- Only `POST /markers` fails randomly (`failure.should_fail`, probability 1/3, `503`).
  Tests monkeypatch that one function. Other endpoints fail only for real reasons.
- One marker, one request at a time: while a `PUT`/`DELETE` is in flight the marker
  is grey and locked (`withMarkerLock` in `markers.ts`). A failed move snaps back.
- Export is a plain link to `GET /markers/export`; the server sets
  `Content-Disposition`, so the download is the server's state, not the client's.
- Import sends the whole file as one `POST /markers/import`; Pydantic validates the
  batch before anything is stored, so it is all-or-nothing. Max 1000 markers per file.
- No database, no auth. `MarkerStore` reads and rewrites one JSON file
  (`MARKERS_FILE`) under a lock on every operation; in Docker it is a volume, on
  Cloud Run a mounted GCS bucket. One shared collection for everyone.

## Deploy

Push to `main` → the `deploy` job in [`ci.yml`](.github/workflows/ci.yml) runs after
lint and tests and ships both services to Cloud Run (`europe-west1`):

- `markers-server` is built by Cloud Build from `server/`, with a GCS bucket mounted
  at `/data` for the markers file and `--max-instances 1`, because one file cannot
  be shared by several writers.
- `markers-client` is built in the workflow (`docker build --build-arg` with the
  Mapbox token and the server URL, both baked into the bundle), pushed to Artifact
  Registry and deployed from that image. The last step puts the client URL into the
  server's `ALLOWED_ORIGINS`.
- Auth is Workload Identity Federation scoped to this repository, no JSON keys.
  GitHub secrets: `GCP_WORKLOAD_IDENTITY_PROVIDER`, `GCP_SERVICE_ACCOUNT`,
  `VITE_MAPBOX_TOKEN`.
- Least privilege: the deployer service account can deploy to Cloud Run and write to
  the two buckets it needs, nothing project-wide; the server runs as its own service
  account that can only read and write the markers bucket.

Everything runs inside the always-free tier; idle services scale to zero.

## Manual test plan

1. Click the map → six colored buttons → pick one → marker appears in that color,
   panel `Total` and the score row go up by one.
2. Repeat a few times: roughly every third attempt shows a red toast
   "Server refused to create marker" and no marker appears.
3. Click a marker → popup with the current score outlined → pick another → color
   and panel update.
4. Drag a marker → it turns grey for the request, then stays. Reload the page:
   the marker is where you left it.
5. Click a marker → Remove → gone, panel updated.
6. Export → `markers.json` downloads with `{"markers": [...]}`.
7. Import that file → markers doubled (ids are ignored, the server assigns new ones).
   Import a broken file → toast, nothing added. Import `{"markers": []}` → grey toast.
8. Clear all → map and panel empty.
9. Stop the server → any action shows "Network error: server is unreachable".
   Start it again → the markers are back (they live in `data/markers.json`).
10. Open http://127.0.0.1:5173 instead of localhost → still works (CORS allows both).

## Known limitations

- **Ghost markers.** If a marker is removed elsewhere (another tab, `Clear all`, the
  file edited by hand) an open page still shows it; edits on it return `404` and a
  toast until the page is reloaded. Handling `404` by removing the marker
  client-side was considered and skipped as out of scope.
- **One writer.** Every request reads and rewrites the whole file, so the server is
  pinned to one instance (`--max-instances 1`); a second instance would overwrite
  the file. Fine for a demo, a real deployment needs a database.
- **Cold starts.** The server scales to zero when idle; the first request after a
  pause takes a couple of seconds.
- **Export bypasses the toast system.** It is a browser navigation; if the server is
  down the browser shows its own error page.
- **DOM markers.** Each marker is a DOM element (`mapboxgl.Marker`), fine up to a few
  hundred, sluggish around a thousand. Beyond that the right tool is a GeoJSON source
  with a circle layer, which would replace most of `markers.ts`.
- **Stats are recomputed from scratch** (six passes) on every change. Deliberate:
  recount from the truth beats incremental counters that can drift.
- **`PUT` is last-write-wins.** Two clients editing the same marker overwrite each
  other; there is no versioning.
- **Import skips failure injection.** Random half-failed imports would need
  partial-success semantics; the batch is atomic instead.
- **Panel is wired directly** (`markers.ts` calls `renderStats`). With a second
  consumer of the marker list it should become a subscription.
- **No dependency injection** for the store or `should_fail`; a module singleton and
  a monkeypatch are enough for one consumer. `Depends` when a second one appears.
