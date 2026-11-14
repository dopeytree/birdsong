# Changelog

## Unreleased

- No station is guessed at. The image used to assume `http://birdnet-go:8080`
  and the Unraid template filled in an address belonging to nobody, so a fresh
  install reported that it could not reach a station that had never been named.
  The page now says there is none yet and shows a sample plate until one is
  given, here or under Settings.

- Plates can be found for creatures that are not birds. Commons files most
  older work beyond birds by genus or by family rather than by species, and
  under two different spellings of the category, so all of them are tried in
  turn and the credit says when a plate is of a relative rather than the
  animal itself. Jardine's Naturalist's Library, British Quadrupeds and
  A History of British Mammals are recognised, which is where the bats are.
  Plates already looked up are forgotten once, since both the asking and the
  ranking have changed.
- Fixed: a hyphenated name did not match its own plate, so a long-tailed tit
  or a black-headed gull lost the bonus for being named. This was found on
  #16 but landed after it was merged.

- A plate found on Wikimedia Commons is now ranked by which animal it shows
  before who drew it. Naming the species counts for more than any hand, so a
  famous plate of the wrong creature no longer wins. Buffon's mammal volumes
  are separated from his birds, plates holding two animals are marked down,
  and a few of the age's animal illustrators are recognised, which matters
  now BirdNET-Go can hear foxes and badgers as well as birds. Skulls and
  brains join the anatomy already turned away. The red fox has a curated
  plate of its own, drawn by Keulemans.
- A plate of a part rather than the whole creature -- a skull, a wing, a
  foot, an egg -- can be offered among the alternatives, under Settings.
  Off by default, and such a plate is never the one chosen first.
- Fixed: no waxwing or lapwing could take a plate from Wikimedia Commons.
  Plates of a wing were turned away by looking for "wing" anywhere in the
  name, which is also how those two birds are spelt.

- Settings can now switch off the title, date, totals, plate number,
  period buttons, the collage and the index, and cap how many species are
  shown.
- The same settings can be put in the address, so one station can feed
  several Home Assistant cards: `?view=plate`, `?view=index` and the
  one-bird views, each showing only its own subject, with `hide=`, `show=`,
  `period=` and `limit=` to adjust them.
- Settings can build a card's address for you, with a live preview
  shaped like a real card. The panel is one narrow column of four sections --
  station, show, card and credits -- of which one is open at a time, so it
  sits on the screen without scrolling. Its paper and the fade behind it
  now match a bird's card, so the two look the same.
- New single-bird views for a small card: `?view=latest` for the bird heard
  most recently, `?view=top` for the one heard most often, `?view=rare` for
  the one heard least. Top and rare give the count and the period, as
  *30 calls over seven days*; the latest bird can show the time it called,
  which is off unless asked for.

- "Station settings" on the page is now simply "Settings"; it holds more
  than the station.

- Fixed: a bird drawn to the very edge of its page came out cut off flat,
  most visibly as a sliced head on some crow plates. Applies to the plates
  Birdsong cuts out itself, not to the Fugleramme artwork.

- The index of species is centred, rather than sitting in the leftmost
  columns of a wide page. Its columns are all the same height, so a short
  list left the ones on the right empty.
- Fixed: on Today, the latest bird was whichever had called most, not the
  one heard last. A day's own figures carry the clock alone, "20:56:36",
  where a longer period carries the whole stamp; the bare clock did not
  parse, so every time read as nothing and the comparison never found a
  winner. The day goes back on them now, which also prints the time in
  the same form as everywhere else.
- Fixed: a bird's description was shown the first time its card was opened
  and never again. The description was written into the card before the card
  was shown, which only worked while the text was still being fetched; once
  it was remembered in the browser it arrived too early and was dropped.

- New: draw the plate from a public BirdWeather station, such as a PUC,
  instead of BirdNET-Go. Set `BIRDWEATHER_STATION` to the station's
  number, or enter it under Settings. nginx forwards `/graphql`
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
