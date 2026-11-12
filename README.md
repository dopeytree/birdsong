# Birdsong

![Birdsong showing a week of detections as a plate of 1800s bird illustrations](docs/screenshot.jpg)

Birdsong draws the birds your [BirdNET-Go](https://github.com/tphakala/birdnet-go)
station has heard as a single plate of hand-cut 1800s illustrations, each
bird sized by how often it called. It is one small Docker container with
one setting. It can also draw from a public
[BirdWeather](https://app.birdweather.com) station, such as a PUC, with no
BirdNET-Go at all.

Created by [Ed Stone](https://ed-stone.co.uk). Current version: 0.42
([changelog](CHANGELOG.md)); images are also tagged by version, e.g. `:0.42`.

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
  fits beneath it without scrolling. Switch it off under Station settings.

## Run it

    docker run -d --name birdsong --restart unless-stopped \
      -p 8095:80 \
      -e BIRDNET_URL=http://192.168.1.50:8080 \
      ghcr.io/dopeytree/birdsong:latest

Then open `http://<your-server>:8095`. `BIRDNET_URL` is the address of
your BirdNET-Go as the container can reach it: use the server's IP, not
`localhost`. That is the only setting.

- **Unraid:** install the template from the terminal, then Docker tab,
  Add Container, and choose `birdsong` under Template:

      wget -O /boot/config/plugins/dockerMan/templates-user/my-birdsong.xml \
        https://raw.githubusercontent.com/dopeytree/birdsong/main/unraid/birdsong.xml

- **Compose:** see `docker-compose.yml`.
- **Preview without a station:** open `/?demo` for a sample plate.

If BirdNET-Go has a password or private mode switched on, allow this
container's address in BirdNET-Go's security settings. Recordings and
spectrograms appear only if BirdNET-Go keeps audio clips, and weather
only if it has a weather provider switched on.

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
also be chosen per browser under Station settings.

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

Add a view to a dashboard, give it the **Grid** layout, then add **Webpage**
cards pointing at Birdsong. Each card carries its own settings in its
address, so one station can feed several cards showing different things.

**Station settings builds the addresses for you.** Under *Home Assistant
card*, pick what the card should show, choose a period and a species limit,
and watch the preview; then copy the address. The rest of this section is
what those addresses mean, if you would rather write them by hand.

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
| `when` | *Heard today at 08:14* or *Least heard: 2 calls* | the one-bird views |

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

    /?view=rare&period=week&hide=sci,when
    the same for the week, picture and name only

    /?view=index&limit=12&show=date
    the twelve most-heard species, under the date

    /?view=plate&show=periods&limit=24&period=month
    a month's collage of 24 birds, with the period buttons

    /?hide=title,number,totals
    the whole page, trimmed of its heading furniture

A card address never shows the settings link, so set the station up on the
main page first. Anything you do not put in the address follows Station
settings for that browser.

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

"Station settings" on the page holds one-screen mode, an optional
BirdNET-Go address override, an optional BirdWeather station (which takes
precedence over both BirdNET-Go and the container's station), and the
credits. These settings, the last
period chosen, and any illustration you pick for a bird are remembered
per browser, not shared between devices.

## Build it yourself

    docker build -t birdsong .
    docker build --build-arg FUGLERAMME_REF=v0.21.3 -t birdsong .   # pin the artwork

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
