# Birdsong

![Birdsong showing a week of detections as a plate of 1800s bird illustrations](docs/screenshot.jpg)

Birdsong draws the birds your [BirdNET-Go](https://github.com/tphakala/birdnet-go)
station has heard as a single plate of hand-cut 1800s illustrations, each
bird sized by how often it called. It is one small Docker container with
one setting. It can also draw from a public
[BirdWeather](https://app.birdweather.com) station, such as a PUC, with no
BirdNET-Go at all.

[![Sponsor](https://img.shields.io/badge/Sponsor-dopeytree-9c3b2e?logo=githubsponsors&logoColor=white)](https://github.com/sponsors/dopeytree)
[![Ko-fi](https://img.shields.io/badge/Ko--fi-dopeytree-9c3b2e?logo=kofi&logoColor=white)](https://ko-fi.com/dopeytree)

Created by [Ed Stone](https://ed-stone.co.uk). Current version: 0.42
([changelog](CHANGELOG.md)); images are also tagged by version, e.g. `:0.42`.

- [Run it](#run-it)
- [Unraid](#unraid)
- [Birdweather Station](#from-a-birdweather-station)
- [Settings](#settings)
- [Home Assistant](#home-assistant)
- [HTTPS with Tailscale](#https-with-tailscale)
- [Credits & License](#credits-and-licences)

## See it in action

[![A tour of Birdsong: the plate over different periods, and the cards for a robin and a little owl](docs/birdsong-v0.42.gif)](docs/birdsong-v0.42.mp4?raw=true)

Shown at double speed; [the full recording](docs/birdsong-v0.42.mp4?raw=true) has sound,
including a little owl heard in the small hours.



## What it shows

- **The plate:** every species heard in the chosen period, sized by its
  number of calls, with an index of species and counts beneath.
- **Periods:** today, seven days (the default), thirty days, or since
  records began. The plate refreshes every minute.
- **A card for each bird**, opened by selecting it:
  - the illustration, with the artist credited
  - a sentence or two about the bird, from Wikipedia
  - calls heard, first and last heard, surest identification, how long
    the species has been known at the station, family, order and how
    common it is locally at this season
  - a note when the bird is new to the station, the year or the season
  - calls by hour of the day, and calls each day for the last thirty days
  - the latest recordings, with the weather at the time, playback and a
    spectrogram
  - other illustrations of the species to choose from
- **One-screen mode** (on by default): the plate shrinks so the index
  fits beneath it without scrolling. Switch it off under Settings.

## Run it

    docker run -d --name birdsong --restart unless-stopped \
      -p 8095:80 \
      -e BIRDNET_URL=http://192.168.1.50:8080 \
      ghcr.io/dopeytree/birdsong:latest

Then open `http://<your-server>:8095`. `BIRDNET_URL` is the address of
your BirdNET-Go as the container can reach it: use the server's IP, not
`localhost`. That is the only setting.

- **Unraid:** see [Unraid](#unraid) below -- it is in the app store.
- **Compose:** see `docker-compose.yml`.
- **Preview without a station:** open `/?demo` for a sample plate.

If BirdNET-Go has a password or private mode switched on, allow this
container's address in BirdNET-Go's security settings. Recordings and
spectrograms appear only if BirdNET-Go keeps audio clips, and weather
only if it has a weather provider switched on.

## Unraid

Birdsong is in Community Applications. Open the **Apps** tab, search for
*birdsong*, and install it. The template sets the port, the data folder
and the icon; the one thing to fill in is **BirdNET-Go address**, which
is your BirdNET-Go as the server sees it, such as
`http://192.168.1.50:8080`. Fill in **BirdWeather station** instead to
draw the plate from a public station. Leave both empty and Birdsong
shows a sample plate until you name one, from the page's own Settings.

The template also maps a **data folder** at `/data`, used only if you
switch on Unraid's per-container Tailscale, which keeps its state there.
See [HTTPS with Tailscale](#https-with-tailscale) if you want to reach
the plate from outside the house, or put it in a Home Assistant card
served over HTTPS.

To install the template by hand -- to try a change before the store has
caught up, say -- fetch it to Unraid's template folder from the terminal,
then go to the Docker tab, Add Container, and choose `birdsong` under
Template:

    wget -O /boot/config/plugins/dockerMan/templates-user/my-birdsong.xml \
      https://raw.githubusercontent.com/dopeytree/Unraid-templates/main/templates/birdsong.xml

The template lives in
[dopeytree/Unraid-templates](https://github.com/dopeytree/Unraid-templates/blob/main/templates/birdsong.xml),
which is the folder the app store reads; it is kept there alone, so there is
one of it rather than two drifting apart.

Community Applications refreshes its templates roughly every two hours,
so a new release takes a little while to show up in the Apps tab.

## From a BirdWeather station

A BirdWeather PUC uploads what it hears to BirdWeather rather than running
BirdNET-Go. To draw its plate, give the station's number instead of
`BIRDNET_URL`: the number at the end of the station's page,
`https://app.birdweather.com/stations/12345`.

    docker run -d --name birdsong --restart unless-stopped \
      -p 8095:80 \
      -e BIRDWEATHER_STATION=12345 \
      ghcr.io/dopeytree/birdsong:latest

The station must be public; no token is needed. nginx forwards `/graphql`
to BirdWeather's public API so the page and its data still share one
address. Any BirdWeather station works, not only a PUC, and a station can
also be chosen per browser under Settings.

BirdWeather has less to say about each bird than BirdNET-Go does. The
plate, the index, calls each day, last heard, how long the species has
been known at the station, and the latest recordings with playback (just
the call, with a second either side) all work. Some things differ:

- **First heard** is a date rather than a time: BirdWeather lists
  detections newest first and can't be asked for the oldest.
- **Calls by hour** covers today or the last seven days. BirdWeather only
  groups by the hour over about a week, so for thirty days and since
  records began the chart shows the last seven days, and says so.
- Family, order, how common the bird is at this season, surest
  identification, the new-to-the-station notes, weather at the time and
  spectrograms are left off the card; BirdWeather doesn't provide them.

## Home Assistant

The birdsong webpages are fully responsive & fully customisable thus suitable for use in homeassistant via the 'webpage' card.

![Homeassistant cards](docs/Screenshot%202026-11-12%20at%2019.09.38.png) 

Click add a new view then paste in the below YAML or create your own

```
type: sections
title: Tablet Home
path: tablet-home
icon: mdi:home-account
sections:
  - type: grid
    cards:
      - type: iframe
        url: https://birdsong.server.ts.net/?view=latest&show=time
        aspect_ratio: 100%
      - type: vertical-stack
        cards:
          - type: iframe
            url: https://birdsong.server.ts.net/?view=index&period=today&limit=15
            aspect_ratio: 100%
  - type: grid
    cards:
      - type: iframe
        url: https://birdsong.server.ts.net/?view=plate&period=today&show=date,totals
        aspect_ratio: 80%
        grid_options:
          rows: 8
          columns: 12
      - type: iframe
        url: https://birdsong.server.ts.net/?view=top&period=week
        aspect_ratio: 50%
```

For full screen - Add a view to a dashboard, give it the **Grid** layout, then add **Webpage**
cards pointing at Birdsong. Each card carries its own settings in its
address, so one station can feed several cards showing different things.

For smaller cards - Create a new webpage card, then paste in your url from the homeassistant card creator in settings on the main birdsong webpage. Or see below for custom. 

![Homeassistant cards creator](docs/Screenshot%202026-11-12%20at%2018.09.04.png) 

**Settings builds the addresses for you.** Open *Settings* on the page,
then *Home Assistant card*: pick the view, tick the parts it should show,
choose a period and a species limit, and watch the preview take the shape
of a real card. Then copy the address. The rest of this section is what
those addresses mean, if you would rather write them by hand.

<!-- Screenshots of the card views belong here. -->

### Views

`?view=` decides what the card is about. Each view shows **only its own
subject** — no title, date, totals or buttons unless you ask for them.

| Address | Card |
|---|---|
| `/` | the whole page, as you see it in a browser |
| `/?view=plate` | the collage of birds, nothing else |
| `/?view=index` | the index of species, nothing else |
| `/?view=latest` | one bird: the last one heard |
| `/?view=top` | one bird: the one heard most in the period |
| `/?view=rare` | one bird: the one heard least in the period |

`latest` is its own window of time, so `period=` does not apply to it.

### Adding and removing parts

`hide=` and `show=` take a comma-separated list. Which names apply depends
on the view:

| Name | What it is | Applies to |
|---|---|---|
| `title` | the word Birdsong | page, collage, index |
| `date` | the date line | page, collage, index |
| `totals` | the species and call totals | page, collage, index |
| `number` | the plate number | page, collage, index |
| `periods` | today / seven days / thirty days / all | page, collage, index |
| `plate` | the collage of birds | page, collage, index |
| `index` | the index of species | page, collage, index |
| `name` | the bird's common name | the one-bird views |
| `sci` | the bird's scientific name | the one-bird views |
| `time` | when it was heard, *1:59 PM* — **off unless asked for** | `latest` |
| `count` | *30 calls over seven days* | `top`, `rare` |

So `?view=index` is the bare index, and `?view=index&show=date,periods`
puts the date and the period buttons back above it. Going the other way,
`?hide=title,number` trims the full page.

### Period and how many species

| Parameter | Does |
|---|---|
| `period=today` `week` `month` `all` | fixes the period for that card, whatever the page is set to |
| `limit=20` | shows only the twenty most-heard species |

`limit` is worth setting on an index card, which otherwise scrolls, and on
a collage card to keep the birds large.

### Examples

    /?view=rare&period=today
    one bird: today's least-heard, with its name and count

    /?view=latest&show=time
    the last bird heard, with the time it called

    /?view=rare&period=week&hide=sci,count
    the week's least-heard, picture and name only

    /?view=index&limit=12&show=date
    the twelve most-heard species, under the date

    /?view=plate&show=periods&limit=24&period=month
    a month's collage of 24 birds, with the period buttons

    /?hide=title,number,totals
    the whole page, trimmed of its heading furniture

A card address never shows the settings link, so set the station up on the
main page first. Anything you do not put in the address follows Settings
for that browser.

If Home Assistant is opened over HTTPS, the browser will refuse to embed a
plain-HTTP page inside it: serve Birdsong over HTTPS (see below) and use
that address in the card instead.

## HTTPS with Tailscale

To give Birdsong an HTTPS address (which the Home Assistant iframe needs
when Home Assistant itself is HTTPS), Unraid's per-container Tailscale
works well:

1. Edit the container and switch on **Use Tailscale**.
2. Tailscale needs a persistent folder for its identity. The template
   ships one: a **Data folder** (`/mnt/user/appdata/birdsong` mapped to
   `/data`), which Tailscale finds on its own, so there is nothing to
   configure. If your container predates the Data folder, or you run
   plain `docker run`, add `-v /mnt/user/appdata/birdsong:/data`.
   Without it, Tailscale refuses to start, and would otherwise join the
   tailnet as a brand-new machine on every update.
3. Enable **Tailscale Serve** with port `80` (the container's internal
   port, not the LAN port), and make sure MagicDNS and HTTPS
   certificates are enabled for your tailnet (Tailscale admin, DNS).

Birdsong is then at `https://birdsong.<your-tailnet>.ts.net` with a real
certificate. Note that only devices on your tailnet can reach that
address; for every device on your LAN instead, put Birdsong behind a
reverse proxy such as Nginx Proxy Manager with its own certificate.

## What is inside the image

- The page (`html/index.html`, plain HTML with no build step) and nginx,
  which also forwards `/api` to BirdNET-Go (or `/graphql` to BirdWeather,
  when `BIRDWEATHER_STATION` is set) so the page and the data share one
  address.
- About 1,400 bird cut-outs covering some 800 species, from the
  [Fugleramme](https://github.com/arnegiacomo/fugleramme) project,
  fetched when the image is built.
- The IM Fell English typeface.

The image is rebuilt every Monday, which is how new Fugleramme artwork
arrives: update the container as you would any other.

## What still comes from the internet

- A bird with no Fugleramme cut-out falls back to an old plate from
  Wikimedia Commons, cut off its page in the browser. Failing that it
  uses BirdNET-Go's (or BirdWeather's) own photo, or just the bird's name.
- The description on each card comes from Wikipedia.

Both are skipped quietly when offline. Everything else is local, unless
the plate is drawn from a BirdWeather station, whose detections and
recordings come from BirdWeather.

## Settings

**Settings** on the page opens a panel of four sections, one open at a
time so the panel stays on the screen:

- **Station** — an optional BirdNET-Go address, overriding `BIRDNET_URL`;
  an optional BirdWeather station, which takes precedence over both
  BirdNET-Go and the container's station; *Save and reload*; and *Show
  the sample plate*, the same sample as `/?demo`.
- **Show** — one-screen mode, then a switch for each part of the page:
  title, date, species and call totals, plate number, period buttons,
  the collage and the index, with *Limit species* to cap how many birds
  are drawn. These are the same parts a card address names with `hide=`
  and `show=`.
- **Home Assistant card** — the card builder above.
- **Credits** — the artwork, the typeface and the sources.

All of this, the last period chosen, and any illustration you pick for a
bird are remembered per browser, not shared between devices. A card
address overrides them for that card alone.

## Trying a creature without waiting for one

Waiting for a tawny owl in order to see how a tawny owl looks is a slow way
to work. `tools/bench.py` stands in for BirdNET-Go: it answers the same
endpoints from a list of creatures you type in. No packages, nothing saved.

    docker build -t birdsong-bench tools/
    docker run -d --name birdsong-bench -p 8099:8099 birdsong-bench

or, without Docker, `python3 tools/bench.py`.

In a compose file beside BirdNET-Go, where it can ask the station what
creatures it knows:

    bench:
      build: https://github.com/dopeytree/birdsong.git#main:tools
      container_name: birdsong-bench
      ports:
        - "8099:8099"
      environment:
        - BENCH_ARGS=--birdnet http://birdnet-go:8080

The container carries the whole species list, fetched when it was built, so it
asks nothing of the network when it runs and needs no Python of your own.

Its page is at `http://localhost:8099`, and that address is what you give
Birdsong: put it under **BirdNET-Go address** in Birdsong's own settings, or
add `?server=http://localhost:8099` to the page's address. Clicking the
address on the bench's page copies it. It has to be reachable from your
browser rather than from inside the container.

Type a few letters of a creature -- `fox`, `tawny`, `pipi` -- and pick it from
the list; it appears on the plate at once. Common names are searched before
scientific ones, and a scientific name you type yourself is used as it stands.
Each row has *again*, to hear it once more just now, and *drop*; *Reset*
empties the list.

The list to search is gathered at startup, and the page says how many
creatures it holds and where they came from. In order:

- a station, if one is named -- the best source, since it knows what your own
  models have been taught, mammals and bats included;
- a `labels.txt` lying in the folder you run it from, or beside the script;
- the BirdNET label list, 6,522 creatures, downloaded once and kept in
  `~/.cache/birdsong-bench/labels.txt`;
- failing all three, the hundred and thirty-odd built in, which cover a
  British garden.

If the download fails -- a Mac's Python often cannot verify TLS until its
certificates are installed -- fetch the list yourself and leave it where the
bench will find it:

    curl -L -o labels.txt https://huggingface.co/tphakala/BirdNET-v2.4/resolve/main/labels.txt

<!-- -->

    python3 tools/bench.py 8099 --birdnet http://192.168.1.50:8080
    python3 tools/bench.py 8099 --labels ./labels.txt     # a list of your own

A list of your own is one `Scientific name_Common name` to a line, which is
how BirdNET writes them. If the download fails the bench says which address
it tried and what went wrong, rather than quietly falling back.

## Build it yourself

    docker build -t birdsong .
    docker build --build-arg FUGLERAMME_REF=v0.21.3 -t birdsong .   # pin the artwork

To try a branch or a pull request before it is merged, build straight from
GitHub and run it on a spare port:

    docker build -t birdsong:test https://github.com/dopeytree/birdsong.git#the-branch
    docker run -d --name birdsong-test -p 8096:80 \
      -e BIRDNET_URL=http://192.168.1.50:8080 birdsong:test

A pull request's branch name is under its title on GitHub, after *wants to
merge ... from*. Remove the test container with
`docker rm -f birdsong-test` when you are done.

To pin a species to an illustration of your choice for everyone, add it
to `CURATED_RAW` near the top of the script in `html/index.html`.

## Credits and licences

- Code in this repository: MIT, see `LICENSE`.
- Bird cut-outs: the *classic* style of Fugleramme by Arne Giacomo,
  after Gould, the von Wright brothers, Audubon and others,
  **CC BY-SA 4.0**. The image carries its `ATTRIBUTION.md` and manifest
  at `/art/`. Keep the credit shown on the page if you change it.
- Icon (`unraid/icon.png`): the robin cut-out from Fugleramme, after
  H. E. Dresser, CC BY-SA 4.0.
- Descriptions: Wikipedia, CC BY-SA.
- Fallback plates: public-domain works on Wikimedia Commons, chiefly
  *Nederlandsche Vogelen* (Nozeman & Sepp, 1770-1829), Koninklijke Bibliotheek.
- Typeface: IM Fell English by Igino Marini, SIL Open Font Licence
  (`html/fonts/OFL.txt`).
- BirdNET-Go is a separate project (CC BY-NC-SA 4.0, non-commercial) and
  is not included.
- BirdWeather is a separate service; detections are read from its public
  API only when a station is given.
