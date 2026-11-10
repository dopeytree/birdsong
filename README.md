# Birdsong

Shows the birds your [BirdNET-Go](https://github.com/tphakala/birdnet-go)
station has heard as a single plate of hand-cut 1800s illustrations, each
bird sized by how often it called. Select a bird for its plate, a short
description, its calls by hour and by day, and its latest recordings.

Created by [Ed Stone](https://ed-stone.co.uk).

## Run it

    docker run -d --name birdsong --restart unless-stopped \
      -p 8095:80 \
      -e BIRDNET_URL=http://192.168.1.50:8080 \
      ghcr.io/dopeytree/birdsong:latest

Then open `http://<your-server>:8095`. `BIRDNET_URL` is the address of
your BirdNET-Go as the container can reach it. That is the only setting.

- **Unraid:** install the template from the terminal, then Docker tab,
  Add Container, and choose `birdsong` under Template:

      wget -O /boot/config/plugins/dockerMan/templates-user/my-birdsong.xml \
        https://raw.githubusercontent.com/dopeytree/birdsong/main/unraid/birdsong.xml
- **Compose:** see `docker-compose.yml`.
- **Preview without a station:** open `/?demo`.

If BirdNET-Go has a password or private mode switched on, allow this
container's address in BirdNET-Go's security settings.

## What is inside the image

- The page (`html/index.html`, no build step) and nginx, which also
  forwards `/api` to BirdNET-Go so the page and the data share one address.
- About 1,400 bird cut-outs from the
  [Fugleramme](https://github.com/arnegiacomo/fugleramme) project,
  fetched when the image is built.
- The IM Fell English typeface.

The image is rebuilt every Monday, which is how new Fugleramme artwork
arrives: update the container as you would any other.

## What still comes from the internet

- A bird with no Fugleramme cut-out falls back to an old plate from
  Wikimedia Commons, cut out in the browser.
- The one- or two-sentence description comes from Wikipedia.

Both are skipped quietly when offline. Everything else is local.

## Settings

"Station settings" on the page holds a one-screen mode and an optional
BirdNET-Go address override. These, and any plate you pick for a bird,
are remembered per browser.

## Build it yourself

    docker build -t birdsong .
    docker build --build-arg FUGLERAMME_REF=v0.21.3 -t birdsong .   # pin the artwork

## Credits and licences

- Code in this repository: MIT, see `LICENSE`.
- Bird cut-outs: the *classic* style of Fugleramme by Arne Giacomo,
  after Gould, the von Wright brothers, Audubon and others,
  **CC BY-SA 4.0**. The image carries its `ATTRIBUTION.md` and manifest
  at `/art/`. Keep the credit shown on the page if you change it.
- Descriptions: Wikipedia, CC BY-SA.
- Fallback plates: public-domain works on Wikimedia Commons, chiefly
  *Nederlandsche Vogelen* (Nozeman & Sepp, 1770-1829), Koninklijke Bibliotheek.
- Icon (`unraid/icon.png`): the robin cut-out from Fugleramme, after
  H. E. Dresser, CC BY-SA 4.0.
- Typeface: IM Fell English by Igino Marini, SIL Open Font Licence
  (`html/fonts/OFL.txt`).
- BirdNET-Go is a separate project (CC BY-NC-SA 4.0, non-commercial) and
  is not included.
