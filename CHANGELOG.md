# Changelog

## Unreleased

- Station settings can now switch off the title, date, totals, plate number,
  period buttons, the collage and the index, and cap how many species are
  shown.
- The same settings can be put in the address, so one station can feed
  several Home Assistant cards: `?view=plate`, `?view=index` and the
  one-bird views, each showing only its own subject, with `hide=`, `show=`,
  `period=` and `limit=` to adjust them.
- Station settings can build a card's address for you, with a live preview
  shaped like a real card. The panel is wider and laid out in two columns.
- New single-bird views for a small card: `?view=latest` for the bird heard
  most recently, `?view=top` for the one heard most often, `?view=rare` for
  the one heard least. Top and rare give the count and the period, as
  *30 calls over seven days*; the latest bird can show the time it called,
  which is off unless asked for.

- Fixed: a bird's description was shown the first time its card was opened
  and never again. The description was written into the card before the card
  was shown, which only worked while the text was still being fetched; once
  it was remembered in the browser it arrived too early and was dropped.

- New: draw the plate from a public BirdWeather station, such as a PUC,
  instead of BirdNET-Go. Set `BIRDWEATHER_STATION` to the station's
  number, or enter it under Station settings. nginx forwards `/graphql`
  to BirdWeather's public API only when the setting is present. The card
  shows what BirdWeather offers: calls by hour and by day, first heard (as
  a date) and last heard, days known at the station, and the latest
  recordings with playback of just the call.
- Fixed: a first-heard date without a time no longer shows as the day
  before for stations west of Greenwich.
- Fixed: the container failed to start with Unraid's per-container
  Tailscale enabled (`nginx: invalid option: "off"`).
- Fixed: a trailing slash on `BIRDNET_URL` is now removed as intended
  (the start-up script was not executable and was being skipped).

## 0.42 — 2026-11-10

First public release.

### The plate
- Every species heard in the chosen period drawn as one plate, each bird
  sized by its number of calls, with an index of species beneath.
- Four periods: today, seven days (the default), thirty days, since
  records began. Refreshes every minute.
- One-screen mode, on by default: the plate shrinks so the index fits
  beneath it with no scrolling.
- Birds never overlap; a strip of clear paper is kept around each.

### Artwork
- About 1,400 hand-cut 1800s illustrations from the Fugleramme project
  (after Gould, the von Wright brothers, Audubon and others) baked into
  the image, covering some 800 species.
- Cut-outs are tinted to the paper colour so their edges blend with the page.
- A bird Fugleramme lacks falls back to a public-domain plate from
  Wikimedia Commons, lifted off its page in the browser; hand-picked
  plates for the collared dove and mute swan.
- Each bird's card offers the other plates of its species to choose from;
  the choice is remembered per browser.

### Bird cards
- A sentence or two about the bird from its Wikipedia article.
- Calls heard, first and last heard, surest identification, days known
  at the station, family, order, and how common the bird is here at this
  season.
- A note when a bird is new to the station, the year or the season.
- Calls by hour of the day, and calls each day over the last thirty days.
- The latest recordings with the weather at the time, playback, and a
  spectrogram of the newest one.

### Container
- One image: the page, its typeface and the artwork, served by nginx,
  which also forwards /api to BirdNET-Go. One setting: BIRDNET_URL.
- Rebuilt weekly to pick up new Fugleramme artwork.
- Unraid template with icon; sample plate at /?demo.
