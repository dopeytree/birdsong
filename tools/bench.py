#!/usr/bin/env python3
"""A stand-in for BirdNET-Go, so a plate can be tried without waiting for a bird.

It answers the handful of endpoints Birdsong reads, from a list of creatures you
type in rather than from a microphone. Point Birdsong at it:

    python3 tools/bench.py
    open http://localhost:8095/?server=http://localhost:8099

Nothing is saved; stop it and the list is gone. Needs no packages.
"""

import json
import re
import sys
import threading
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8099

# sci -> {"common": str, "count": int, "last": datetime, "first": datetime}
HEARD = {}
LOCK = threading.Lock()

PRESETS = [
    ("Red Fox", "Vulpes vulpes"),
    ("European Badger", "Meles meles"),
    ("Common Pipistrelle", "Pipistrellus pipistrellus"),
    ("Tawny Owl", "Strix aluco"),
    ("European Robin", "Erithacus rubecula"),
    ("Bohemian Waxwing", "Bombycilla garrulus"),
    ("Long-tailed Tit", "Aegithalos caudatus"),
    ("Western European Hedgehog", "Erinaceus europaeus"),
]


def hear(sci, common, count=None, when=None):
    """Record a creature as heard now, or adjust what is already there."""
    now = when or datetime.now()
    with LOCK:
        row = HEARD.get(sci)
        if row is None:
            HEARD[sci] = {"common": common or sci, "count": count or 1, "first": now, "last": now}
        else:
            if common:
                row["common"] = common
            row["count"] = count if count is not None else row["count"] + 1
            row["last"] = now


def rows_summary():
    out = []
    for sci, r in sorted(HEARD.items(), key=lambda kv: -kv[1]["count"]):
        out.append({
            "scientific_name": sci,
            "common_name": r["common"],
            "count": r["count"],
            # BirdNET-Go stamps these with the real offset for the date
            "first_heard": r["first"].astimezone().isoformat(timespec="seconds"),
            "last_heard": r["last"].astimezone().isoformat(timespec="seconds"),
            "avg_confidence": 0.84,
            "max_confidence": 0.99,
        })
    return out


def rows_daily():
    out = []
    for sci, r in sorted(HEARD.items(), key=lambda kv: -kv[1]["count"]):
        hours = [0] * 24
        hours[r["last"].hour] = r["count"]
        out.append({
            "scientific_name": sci,
            "common_name": r["common"],
            "count": r["count"],
            "hourly_counts": hours,
            "high_confidence": True,
            "max_confidence": 0.99,
            # the daily endpoint gives the clock alone, with no date on it
            "first_heard": r["first"].strftime("%H:%M:%S"),
            "latest_heard": r["last"].strftime("%H:%M:%S"),
        })
    return out


def rows_detections(sci, limit):
    r = HEARD.get(sci)
    if not r:
        return []
    out = []
    for i in range(min(limit, r["count"])):
        t = r["last"] - timedelta(minutes=7 * i)
        out.append({
            "id": None,          # no id: no spectrogram or audio is offered
            "scientificName": sci,
            "commonName": r["common"],
            "date": t.strftime("%Y-%m-%d"),
            "time": t.strftime("%H:%M:%S"),
            "confidence": 0.9,
            "spectrogramOnly": True,
        })
    return out


PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Birdsong bench</title>
<style>
  :root { --paper:#efe9d8; --ink:#2a241c; --rule:#c9bda0; --madder:#9c3b2e; }
  * { box-sizing:border-box }
  body { margin:0; padding:2rem 1.5rem; background:var(--paper); color:var(--ink);
         font:16px/1.5 "Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif }
  main { max-width:46rem; margin:0 auto }
  h1 { font-weight:400; font-size:1.8rem; margin:0 0 .2rem }
  p.sub { margin:0 0 1.6rem; color:#6b5e49 }
  fieldset { border:1px solid var(--rule); margin:0 0 1.4rem; padding:.8rem 1rem 1rem }
  legend { font-size:.85rem; letter-spacing:.08em; text-transform:uppercase; padding:0 .4rem }
  label { display:block; font-size:.9rem; margin:.6rem 0 .15rem }
  input { font:inherit; padding:.4rem .5rem; border:1px solid var(--rule); background:#fbf7ec;
          color:inherit; width:100% }
  .row { display:flex; gap:.7rem; flex-wrap:wrap; align-items:flex-end }
  .row > div { flex:1 1 12rem }
  .row > div.narrow { flex:0 0 7rem }
  button { font:inherit; padding:.42rem .9rem; border:1px solid var(--rule); background:#fbf7ec;
           color:inherit; cursor:pointer }
  button:hover { border-color:var(--madder); color:var(--madder) }
  button.go { border-color:var(--madder); color:var(--madder) }
  .presets { display:flex; gap:.4rem; flex-wrap:wrap; margin-top:.2rem }
  .presets button { font-size:.85rem; padding:.25rem .6rem }
  table { width:100%; border-collapse:collapse; margin-top:.4rem }
  th { text-align:left; font-weight:400; font-size:.8rem; letter-spacing:.06em;
       text-transform:uppercase; color:#6b5e49; border-bottom:1px solid var(--rule); padding:.3rem .4rem }
  td { padding:.35rem .4rem; border-bottom:1px solid #ded2b6 }
  td i { color:#6b5e49 }
  td.n { text-align:right; font-variant-numeric:tabular-nums }
  .empty { color:#6b5e49; padding:.8rem .4rem }
  code { background:#fbf7ec; padding:.1rem .3rem; border:1px solid var(--rule) }
  .note { font-size:.85rem; color:#6b5e49; margin:.5rem 0 0 }
  #said { min-height:1.2rem; font-size:.9rem; color:var(--madder); margin:.5rem 0 0 }
</style></head><body><main>

<h1>Birdsong bench</h1>
<p class="sub">A stand-in for BirdNET-Go. Name a creature, and Birdsong will draw it.</p>

<fieldset>
  <legend>Open Birdsong against this</legend>
  <p style="margin:.3rem 0"><code id="url">…</code></p>
  <p class="note">Change the port if Birdsong is served somewhere else. The address has to
     be reachable from your browser, not from the container.</p>
</fieldset>

<fieldset>
  <legend>Heard just now</legend>
  <div class="row">
    <div><label for="common">Common name</label><input id="common" placeholder="Red Fox"></div>
    <div><label for="sci">Scientific name</label><input id="sci" placeholder="Vulpes vulpes"></div>
    <div class="narrow"><label for="count">Calls</label><input id="count" type="number" min="1" value="1"></div>
    <div class="narrow"><button class="go" id="add">Heard it</button></div>
  </div>
  <p class="note">Fill in one name and press <b>Look up</b> to find the other, or type both.
     Birdsong draws by scientific name.</p>
  <div class="presets" style="margin-top:.6rem">
    <button id="lookup">Look up</button>
    __PRESETS__
  </div>
  <div id="said"></div>
</fieldset>

<fieldset>
  <legend>What has been heard</legend>
  <div id="list"></div>
  <div class="row" style="margin-top:.8rem">
    <div class="narrow"><button id="reset">Reset</button></div>
  </div>
</fieldset>

</main><script>
const $ = s => document.querySelector(s);
const say = t => { $("#said").textContent = t; };

$("#url").textContent = "http://localhost:8095/?server=" + location.origin;

async function load() {
  const r = await fetch("/bench/state").then(r => r.json());
  if (!r.length) { $("#list").innerHTML = '<p class="empty">Nothing yet.</p>'; return; }
  $("#list").innerHTML = '<table><tr><th>Creature</th><th>Scientific name</th>' +
    '<th class="n">Calls</th><th class="n">Last</th><th></th></tr>' +
    r.map(x => '<tr><td>' + esc(x.common) + '</td><td><i>' + esc(x.sci) + '</i></td>' +
      '<td class="n">' + x.count + '</td><td class="n">' + x.last + '</td>' +
      '<td class="n"><button data-again="' + esc(x.sci) + '">again</button> ' +
      '<button data-drop="' + esc(x.sci) + '">drop</button></td></tr>').join("") + '</table>';
}
const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;" }[c]));

async function post(path, body) {
  await fetch(path, { method: "POST", headers: { "Content-Type": "application/json" },
                      body: JSON.stringify(body || {}) });
  load();
}

$("#add").addEventListener("click", () => {
  const sci = $("#sci").value.trim(), common = $("#common").value.trim();
  if (!sci) return say("A scientific name is what Birdsong draws by.");
  post("/bench/hear", { sci, common, count: Number($("#count").value) || 1 });
  say("Heard " + (common || sci) + ".");
});

$("#reset").addEventListener("click", () => { post("/bench/reset"); say("Cleared."); });

$("#list").addEventListener("click", e => {
  const again = e.target.dataset.again, drop = e.target.dataset.drop;
  if (again) post("/bench/hear", { sci: again });
  if (drop) post("/bench/drop", { sci: drop });
});

document.querySelector(".presets").addEventListener("click", e => {
  const p = e.target.dataset.preset;
  if (!p) return;
  const [common, sci] = p.split("|");
  $("#common").value = common; $("#sci").value = sci;
  post("/bench/hear", { sci, common, count: Number($("#count").value) || 1 });
  say("Heard " + common + ".");
});

// Wikidata knows the binomial for a common name, and the other way round
$("#lookup").addEventListener("click", async () => {
  const typed = $("#sci").value.trim() || $("#common").value.trim();
  if (!typed) return say("Type a name first.");
  say("Looking…");
  try {
    const s = await fetch("https://www.wikidata.org/w/api.php?action=wbsearchentities&format=json&origin=*" +
      "&language=en&limit=5&search=" + encodeURIComponent(typed)).then(r => r.json());
    for (const hit of s.search || []) {
      const e = await fetch("https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&origin=*" +
        "&props=claims|labels&languages=en&ids=" + hit.id).then(r => r.json());
      const ent = e.entities[hit.id];
      const taxon = ((ent.claims || {}).P225 || [])[0];
      if (!taxon) continue;
      $("#sci").value = taxon.mainsnak.datavalue.value;
      $("#common").value = (ent.labels.en || {}).value || $("#common").value;
      return say("Found " + $("#sci").value + ".");
    }
    say("No creature of that name on Wikidata. Type the scientific name yourself.");
  } catch (err) { say("Wikidata could not be reached."); }
});

load();
setInterval(load, 4000);
</script></body></html>
"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def reply(self, body, ctype="application/json", code=200):
        if not isinstance(body, bytes):
            body = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Accept")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.reply(b"", "text/plain")

    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        p = u.path
        if p == "/":
            buttons = "".join(
                '<button data-preset="%s|%s">%s</button>' % (c, s, c) for c, s in PRESETS)
            return self.reply(PAGE.replace("__PRESETS__", buttons), "text/html")
        if p == "/bench/state":
            with LOCK:
                out = [{"sci": k, "common": v["common"], "count": v["count"],
                        "last": v["last"].strftime("%H:%M:%S")}
                       for k, v in sorted(HEARD.items(), key=lambda kv: -kv[1]["count"])]
            return self.reply(json.dumps(out))
        if p.startswith("/api/v2/analytics/species/daily"):
            return self.reply(json.dumps(rows_daily()))
        if p.startswith("/api/v2/analytics/species/summary"):
            return self.reply(json.dumps(rows_summary()))
        if p.startswith("/api/v2/detections"):
            sci = (q.get("species") or [""])[0]
            n = int((q.get("numResults") or ["5"])[0])
            return self.reply(json.dumps(rows_detections(sci, n)))
        if p.startswith("/api/"):
            return self.reply(json.dumps([]))        # anything else: nothing heard
        self.reply(b"not here", "text/plain", 404)

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        try:
            body = json.loads(self.rfile.read(n) or b"{}")
        except ValueError:
            body = {}
        p = urlparse(self.path).path
        if p == "/bench/hear":
            sci = re.sub(r"\s+", " ", str(body.get("sci", "")).strip())
            if sci:
                hear(sci, str(body.get("common", "")).strip(), body.get("count"))
            return self.reply(b'{"ok":true}')
        if p == "/bench/drop":
            with LOCK:
                HEARD.pop(str(body.get("sci", "")), None)
            return self.reply(b'{"ok":true}')
        if p == "/bench/reset":
            with LOCK:
                HEARD.clear()
            return self.reply(b'{"ok":true}')
        self.reply(b"not here", "text/plain", 404)


if __name__ == "__main__":
    print("Birdsong bench on http://localhost:%d" % PORT)
    print("Open Birdsong against it: http://localhost:8095/?server=http://localhost:%d" % PORT)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
