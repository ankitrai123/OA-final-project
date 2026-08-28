# Service Line — Restaurant Operations Console

A single-page dashboard for the operations analytics project. Seven pages, no scrolling,
switched by the tabs at the top or the number keys.

## Running it

Open a terminal in this folder and start a local server:

```
python -m http.server 8000
```

Then visit **http://localhost:8000** in your browser.

Opening `index.html` directly by double-clicking will display everything correctly, but the
AI analyst will fail — browsers block API calls from `file://` pages. Use the server.

Chart.js and SheetJS are bundled in `vendor/`, so the dashboard works with no internet.
Only the AI analyst needs a connection.

## Hosting on your intranet

Run `python serve.py` instead of the plain `http.server` command above — it listens on every
network interface, not just this machine, and prints the URL to hand out:

```
Service Line running at:
  http://localhost:8000          (this machine)
  http://192.168.1.42:8000       (share this on your intranet)
```

Anyone on the same network can then open that second URL in their browser. Two things to check:

- Open port 8000 to inbound connections in the host machine's firewall (Windows Firewall, `ufw`,
  etc.) — most block it by default.
- Everyone reaches the AI relay (`/api`) too, since it's the same server. It only forwards to the
  five providers in `ALLOWED_HOSTS` and still needs a valid key in the request, but there's no
  login in front of it — fine for a trusted classroom/office network during a demo, not something
  to leave running unattended on an open network.

## Pages

| Key | Page | What it does |
|-----|------|--------------|
| 1 | Line | The four headline decisions, kept in sync with the model pages |
| 2 | Pairs | Association rules — lift, support, confidence |
| 3 | Demand | Twelve-week cold coffee forecast and how the model was chosen |
| 4 | Prep | Live newsvendor — drag the sliders, the target recalculates |
| 5 | Stock | Service level slider and the cost curve of higher cover |
| 6 | Supply | Optimal supplier plan, solved live, plus capacity sensitivity |
| 7 | Analyst | Ask Claude about the numbers currently on screen |

`←` `→` step between pages. `Esc` leaves a text field.

## Excel

**Load Excel** reads a workbook and looks for rows whose first cell names a supplier
(*Local*, *City*, *Metro*) followed by four unit costs and a capacity, plus a row whose
first cell contains *demand*. `Restaurant_Supply_Network_Solver.xlsx` works as-is. Change a
cost in Excel, reload the file, and the optimal plan re-solves in front of the room.

**Export plan** writes `operations_plan.xlsx` containing the current allocation, the weekly
cost, and your prep and stock parameters.

The supplier plan is solved by minimum-cost flow, so the allocation shown is the true
optimum for whatever costs and capacities are loaded — not a stored answer. With the
baseline file it reproduces ₹15,15,850.

## The AI analyst

Paste an Anthropic API key on the Analyst page. Every question is sent with a JSON snapshot
of the live dashboard state, so answers cite your actual numbers rather than guessing.

**About the key:** it lives in the tab's memory only. It is never written into this file,
into browser storage, or to disk, and it is gone when you close the tab. Because the browser
calls Anthropic directly, the key does travel from your machine — fine for a local demo, but
regenerate it at console.anthropic.com after your presentation.

### Using Ollama instead of a cloud key

If your network blocks outbound calls to the AI providers (common on locked-down campus/office
intranets), pick **Ollama (local)** from the Provider dropdown. It needs no API key and never
leaves the network:

1. Install [Ollama](https://ollama.com) and pull a model, e.g. `ollama pull llama3.2`.
2. Leave the key field blank — it defaults to `http://localhost:11434`. Only fill it in if
   Ollama is running elsewhere, e.g. `http://192.168.1.42:11434` for one shared instance on
   your intranet.
3. Ask a question as usual.

If you get a CORS-style failure on the first try, Ollama's default origin allowlist doesn't
include this page. Restart Ollama with `OLLAMA_ORIGINS=*` set (or list this dashboard's exact
origin) and it'll allow the direct browser call. Failing that, `serve.py`'s relay (`/api`) will
proxy to `localhost` and private-network addresses automatically — the fixed-provider allowlist
doesn't apply there.

## Files

```
index.html                  the whole dashboard
vendor/chart.umd.js         charts
vendor/xlsx.full.min.js     Excel read/write
```
