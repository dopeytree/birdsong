# ---- stage 1: fetch the Fugleramme artwork (CC BY-SA 4.0) -------------------
FROM alpine/git AS art
ARG FUGLERAMME_REF=main
RUN git clone --depth 1 --branch "${FUGLERAMME_REF}" https://github.com/arnegiacomo/fugleramme /src \
 && mkdir -p /art/artwork \
 && cp -r /src/assets/artwork/classic /art/artwork/classic \
 && cp /src/assets/birdnet_aliases.json /src/assets/ATTRIBUTION.md /art/ \
 && git -C /src rev-parse HEAD > /art/FUGLERAMME_COMMIT

# ---- stage 2: the page, the artwork and a small web server ------------------
FROM nginx:alpine
ENV BIRDNET_URL=http://birdnet-go:8080
COPY nginx/default.conf.template /etc/nginx/templates/default.conf.template
COPY nginx/05-birdnet-url.envsh /docker-entrypoint.d/05-birdnet-url.envsh
COPY html/ /usr/share/nginx/html/
COPY --from=art /art/ /usr/share/nginx/html/art/
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://127.0.0.1/healthz || exit 1
