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
COPY --chmod=755 nginx/05-birdnet-url.envsh /docker-entrypoint.d/05-birdnet-url.envsh
COPY html/ /usr/share/nginx/html/
COPY --from=art /art/ /usr/share/nginx/html/art/
# Keep nginx in the foreground from its config rather than the usual
# `-g "daemon off;"` argument: wrappers that re-launch the command (Unraid's
# Tailscale hook) split that argument at the space and nginx refuses to start.
RUN sed -i '1i daemon off;' /etc/nginx/nginx.conf
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://127.0.0.1/healthz || exit 1
CMD ["nginx"]
