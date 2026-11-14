# Birdsong

Birdsong draws the birds your BirdNET-Go station has heard as a single plate
of hand-cut 1800s illustrations, each bird sized by how often it called.

## Setting it up

On the **Configuration** tab, fill in one of these, then start the app:

- **BirdNET-Go address**: your BirdNET-Go as Home Assistant can reach it,
  such as `http://192.168.1.50:8080`. Use the IP address, not `localhost`.
- **BirdWeather station**: the number of a public BirdWeather station, from
  the end of its page, `https://app.birdweather.com/stations/12345`.

Leave both empty and Birdsong shows a sample plate until you name one.

If BirdNET-Go has a password or private mode switched on, allow Home
Assistant's address in BirdNET-Go's security settings.

The page is on port 8096 of your Home Assistant host. **Open web UI** takes you
there. Change the port on the **Network** tab if 8096 is taken.

## Cards on a dashboard

Birdsong's views fit Home Assistant's **Webpage** card. Open Birdsong, then
**Settings > Home Assistant card** to build a card address and copy it. The
README lists every view and option:
https://github.com/dopeytree/birdsong#home-assistant

If you open Home Assistant over HTTPS, the browser won't show a plain-HTTP
page inside a card. Put Birdsong behind the same HTTPS proxy, or see "HTTPS
with Tailscale" in the README.
