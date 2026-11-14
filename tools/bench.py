#!/usr/bin/env python3
"""A stand-in for BirdNET-Go, so a plate can be tried without waiting for a bird.

It answers the handful of endpoints Birdsong reads, from a list of creatures you
type in rather than from a microphone. Point Birdsong at it:

    python3 tools/bench.py                       # or: bench.py 8099 --birdnet http://pi:8080

and give Birdsong the bench's address, under its own settings or as
?server=http://localhost:8099

Nothing is saved; stop it and the list is gone. Needs no packages.
"""

import json
import re
import sys
import threading
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

PORT = next((int(a) for a in sys.argv[1:] if a.isdigit()), 8099)   # bench.py [port] [--birdnet URL]

# sci -> {"common": str, "count": int, "last": datetime, "first": datetime}
HEARD = {}
LOCK = threading.Lock()

# A list to search, so a name need not be spelt from memory. Three sources, in
# order: a BirdNET-Go if one is named on the command line, the published label
# list if it can be fetched, and failing both, the creatures below.
LABEL_URLS = [
    "https://raw.githubusercontent.com/birdnet-team/BirdNET-Analyzer/main/birdnet_analyzer/labels/V2.4/BirdNET_GLOBAL_6K_V2.4_Labels.txt",
    "https://raw.githubusercontent.com/kahst/BirdNET-Analyzer/main/checkpoints/V2.4/BirdNET_GLOBAL_6K_V2.4_Labels.txt",
    "https://raw.githubusercontent.com/tphakala/birdnet-go/main/internal/birdnet/data/labels/en-uk.txt",
]

BUILT_IN = """European Robin|Erithacus rubecula
Eurasian Blackbird|Turdus merula
Song Thrush|Turdus philomelos
Mistle Thrush|Turdus viscivorus
Redwing|Turdus iliacus
Fieldfare|Turdus pilaris
Eurasian Blue Tit|Cyanistes caeruleus
Great Tit|Parus major
Coal Tit|Periparus ater
Long-tailed Tit|Aegithalos caudatus
Marsh Tit|Poecile palustris
Eurasian Wren|Troglodytes troglodytes
Dunnock|Prunella modularis
House Sparrow|Passer domesticus
Eurasian Tree Sparrow|Passer montanus
Common Chaffinch|Fringilla coelebs
Brambling|Fringilla montifringilla
European Greenfinch|Chloris chloris
European Goldfinch|Carduelis carduelis
Eurasian Siskin|Spinus spinus
Common Linnet|Linaria cannabina
Eurasian Bullfinch|Pyrrhula pyrrhula
Hawfinch|Coccothraustes coccothraustes
Common Starling|Sturnus vulgaris
Common Magpie|Pica pica
Eurasian Jay|Garrulus glandarius
Eurasian Jackdaw|Coloeus monedula
Rook|Corvus frugilegus
Carrion Crow|Corvus corone
Common Raven|Corvus corax
Common Wood-Pigeon|Columba palumbus
Stock Dove|Columba oenas
Collared Dove|Streptopelia decaocto
Rock Pigeon|Columba livia
Tawny Owl|Strix aluco
Barn Owl|Tyto alba
Little Owl|Athene noctua
Long-eared Owl|Asio otus
Short-eared Owl|Asio flammeus
Common Buzzard|Buteo buteo
Red Kite|Milvus milvus
Eurasian Sparrowhawk|Accipiter nisus
Common Kestrel|Falco tinnunculus
Peregrine Falcon|Falco peregrinus
Ring-necked Pheasant|Phasianus colchicus
Grey Heron|Ardea cinerea
Little Egret|Egretta garzetta
Western Cattle-Egret|Ardea ibis
Great Bittern|Botaurus stellaris
Mute Swan|Cygnus olor
Whooper Swan|Cygnus cygnus
Canada Goose|Branta canadensis
Greylag Goose|Anser anser
Mallard|Anas platyrhynchos
Tufted Duck|Aythya fuligula
Common Shelduck|Tadorna tadorna
Ruddy Shelduck|Tadorna ferruginea
Common Moorhen|Gallinula chloropus
Eurasian Coot|Fulica atra
Water Rail|Rallus aquaticus
Northern Lapwing|Vanellus vanellus
Eurasian Curlew|Numenius arquata
Eurasian Oystercatcher|Haematopus ostralegus
European Golden Plover|Pluvialis apricaria
Grey Plover|Pluvialis squatarola
Eurasian Woodcock|Scolopax rusticola
Common Snipe|Gallinago gallinago
Black-headed Gull|Chroicocephalus ridibundus
Herring Gull|Larus argentatus
Common Gull|Larus canus
Common Swift|Apus apus
Barn Swallow|Hirundo rustica
House Martin|Delichon urbicum
Sand Martin|Riparia riparia
Common Chiffchaff|Phylloscopus collybita
Willow Warbler|Phylloscopus trochilus
Eurasian Blackcap|Sylvia atricapilla
Garden Warbler|Sylvia borin
Common Whitethroat|Curruca communis
Goldcrest|Regulus regulus
Common Firecrest|Regulus ignicapilla
Eurasian Nuthatch|Sitta europaea
Eurasian Treecreeper|Certhia familiaris
Great Spotted Woodpecker|Dendrocopos major
Lesser Spotted Woodpecker|Dryobates minor
Eurasian Green Woodpecker|Picus viridis
Black Woodpecker|Dryocopus martius
Common Kingfisher|Alcedo atthis
Pied Wagtail|Motacilla alba
Grey Wagtail|Motacilla cinerea
Meadow Pipit|Anthus pratensis
Eurasian Skylark|Alauda arvensis
Yellowhammer|Emberiza citrinella
Reed Bunting|Emberiza schoeniclus
Common Cuckoo|Cuculus canorus
Bohemian Waxwing|Bombycilla garrulus
Common Redstart|Phoenicurus phoenicurus
European Stonechat|Saxicola rubicola
Common Nightingale|Luscinia megarhynchos
Red-billed Chough|Pyrrhocorax pyrrhocorax
Red Fox|Vulpes vulpes
European Badger|Meles meles
Western European Hedgehog|Erinaceus europaeus
European Rabbit|Oryctolagus cuniculus
European Hare|Lepus europaeus
Eastern Grey Squirrel|Sciurus carolinensis
Red Squirrel|Sciurus vulgaris
Roe Deer|Capreolus capreolus
Red Deer|Cervus elaphus
Fallow Deer|Dama dama
Reeves's Muntjac|Muntiacus reevesi
Stoat|Mustela erminea
Least Weasel|Mustela nivalis
European Otter|Lutra lutra
European Pine Marten|Martes martes
European Mole|Talpa europaea
Common Shrew|Sorex araneus
Wood Mouse|Apodemus sylvaticus
Brown Rat|Rattus norvegicus
Field Vole|Microtus agrestis
Common Pipistrelle|Pipistrellus pipistrellus
Soprano Pipistrelle|Pipistrellus pygmaeus
Nathusius's Pipistrelle|Pipistrellus nathusii
Common Noctule|Nyctalus noctula
Leisler's Bat|Nyctalus leisleri
Serotine Bat|Eptesicus serotinus
Brown Long-eared Bat|Plecotus auritus
Daubenton's Bat|Myotis daubentonii
Natterer's Bat|Myotis nattereri
Whiskered Bat|Myotis mystacinus
Greater Horseshoe Bat|Rhinolophus ferrumequinum
Lesser Horseshoe Bat|Rhinolophus hipposideros
Western Barbastelle|Barbastella barbastellus
Common Frog|Rana temporaria
Common Toad|Bufo bufo
Marsh Frog|Pelophylax ridibundus
Natterjack Toad|Epidalea calamita"""

KNOWN = []          # [(common, sci)]
KNOWN_FROM = "the built-in list"


def load_known(birdnet=None):
    """Gather the creatures that can be searched for."""
    global KNOWN, KNOWN_FROM
    seen, out, where = set(), [], []

    def add(common, sci):
        sci = sci.strip()
        if sci and sci.lower() not in seen:
            seen.add(sci.lower())
            out.append((common.strip() or sci, sci))

    if birdnet:
        try:
            import urllib.request
            u = birdnet.rstrip("/") + "/api/v2/analytics/species/summary"
            with urllib.request.urlopen(u, timeout=10) as r:
                for row in json.loads(r.read()):
                    add(row.get("common_name", ""), row.get("scientific_name", ""))
            where.append("%d from %s" % (len(out), birdnet))
        except Exception as e:
            print("  could not read %s (%s)" % (birdnet, e))

    before = len(out)
    for url in LABEL_URLS:
        try:
            import urllib.request
            with urllib.request.urlopen(url, timeout=20) as r:
                for line in r.read().decode("utf8").splitlines():
                    if "_" in line:
                        sci, common = line.split("_", 1)
                        add(common, sci)
            where.append("%d from the published labels" % (len(out) - before))
            break
        except Exception:
            continue

    before = len(out)
    for line in BUILT_IN.splitlines():
        common, sci = line.split("|")
        add(common, sci)
    if len(out) - before:
        where.append("%d built in" % (len(out) - before))

    KNOWN = out
    KNOWN_FROM = ", ".join(where) or "nothing"
    print("  searching %d creatures: %s" % (len(KNOWN), KNOWN_FROM))


def search(q, limit=12):
    """Common name first, and a name that starts with what was typed first of all."""
    q = q.strip().lower()
    if not q:
        return []
    hits = []
    for common, sci in KNOWN:
        c, s = common.lower(), sci.lower()
        if c.startswith(q):
            rank = 0
        elif any(w.startswith(q) for w in re.split(r"[\s-]+", c)):
            rank = 1
        elif s.startswith(q):
            rank = 2
        elif q in c:
            rank = 3
        elif q in s:
            rank = 4
        else:
            continue
        hits.append((rank, len(common), common, sci))
    hits.sort()
    return [{"common": c, "sci": s} for _, _, c, s in hits[:limit]]


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
  #hits { margin-top:.6rem }
  #hits button { display:block; width:100%; text-align:left; border:0; border-bottom:1px solid #ded2b6;
                 background:none; padding:.35rem .4rem }
  #hits button:hover, #hits button:focus { background:#fbf7ec; color:var(--madder) }
  #hits i { color:#6b5e49 }
  #url { cursor:pointer }
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
  <legend>Give this address to Birdsong</legend>
  <p style="margin:.3rem 0"><code id="url" title="Click to copy">…</code>
     <span id="copied" class="note"></span></p>
  <p class="note">Put it in Birdsong's settings under <b>BirdNET-Go address</b>, or add it to
     the page's address as <code>?server=</code>. It has to be reachable from your browser,
     not from inside the container.</p>
</fieldset>

<fieldset>
  <legend>Heard just now</legend>
  <div class="row">
    <div><label for="q">Creature</label><input id="q" autocomplete="off" placeholder="fox, tawny, pipistrelle…"></div>
    <div class="narrow"><label for="count">Calls</label><input id="count" type="number" min="1" value="1"></div>
  </div>
  <div id="hits"></div>
  <div id="said"></div>
  <p class="note" id="from"></p>
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

$("#url").textContent = location.origin;
$("#url").addEventListener("click", async () => {
  try { await navigator.clipboard.writeText(location.origin); $("#copied").textContent = "copied"; }
  catch (e) { $("#copied").textContent = "select it and copy"; }
  setTimeout(() => $("#copied").textContent = "", 1800);
});

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

let timer;
$("#q").addEventListener("input", () => { clearTimeout(timer); timer = setTimeout(look, 150); });
$("#q").addEventListener("keydown", e => {
  if (e.key === "Enter") { const first = $("#hits button"); if (first) first.click(); }
});

async function look() {
  const q = $("#q").value.trim();
  if (!q) { $("#hits").innerHTML = ""; return; }
  const r = await fetch("/bench/search?q=" + encodeURIComponent(q)).then(r => r.json());
  $("#hits").innerHTML = r.length
    ? r.map(x => '<button data-sci="' + esc(x.sci) + '" data-common="' + esc(x.common) + '">' +
        esc(x.common) + ' &nbsp;<i>' + esc(x.sci) + '</i></button>').join("")
    : '<p class="empty">Nothing of that name. Type a scientific name to use it anyway.</p>';
}

$("#hits").addEventListener("click", e => {
  const b = e.target.closest("button[data-sci]");
  if (!b) return;
  post("/bench/hear", { sci: b.dataset.sci, common: b.dataset.common,
                        count: Number($("#count").value) || 1 });
  say("Heard " + b.dataset.common + ".");
  $("#q").value = ""; $("#hits").innerHTML = ""; $("#q").focus();
});

$("#reset").addEventListener("click", () => { post("/bench/reset"); say("Cleared."); });

$("#list").addEventListener("click", e => {
  const again = e.target.dataset.again, drop = e.target.dataset.drop;
  if (again) post("/bench/hear", { sci: again });
  if (drop) post("/bench/drop", { sci: drop });
});



fetch("/bench/from").then(r => r.json()).then(d => {
  $("#from").textContent = d.count + " creatures to search: " + d.from + ".";
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
            return self.reply(PAGE, "text/html")
        if p == "/bench/search":
            return self.reply(json.dumps(search((q.get("q") or [""])[0])))
        if p == "/bench/from":
            return self.reply(json.dumps({"from": KNOWN_FROM, "count": len(KNOWN)}))
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
    birdnet = ""
    for i, a in enumerate(sys.argv):
        if a == "--birdnet" and i + 1 < len(sys.argv):
            birdnet = sys.argv[i + 1]
    print("Birdsong bench on http://localhost:%d" % PORT)
    load_known(birdnet or None)
    print("Give this address to Birdsong: http://localhost:%d" % PORT)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
