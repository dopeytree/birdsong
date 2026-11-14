# The bench: a stand-in for BirdNET-Go, so a plate can be tried without
# waiting for a bird.
#
#   docker build -t birdsong-bench tools/
#   docker run -d --name birdsong-bench -p 8099:8099 birdsong-bench
#
# The species list is fetched here, at build, so the container needs nothing
# from the network when it runs and no machine needs its own Python in order.
FROM python:3.12-alpine

WORKDIR /app

# 6,522 creatures, "Scientific name_Common name" to a line. Change this to
# another list, or mount your own over /app/labels.txt, if you would rather.
ARG LABELS=https://huggingface.co/tphakala/BirdNET-v2.4/resolve/main/labels.txt
RUN set -eu; \
    wget -qO /app/labels.txt "$LABELS"; \
    n=$(grep -c "_" /app/labels.txt || true); \
    [ "$n" -gt 1000 ] || { echo "that address gave $n names, which is not the list"; exit 1; }; \
    echo "labels: $n creatures"

COPY bench.py /app/bench.py

EXPOSE 8099
HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://127.0.0.1:8099/bench/from || exit 1

# BENCH_ARGS passes the rest through, e.g. --birdnet http://birdnet-go:8080
ENV BENCH_ARGS=""
CMD ["sh", "-c", "python3 /app/bench.py 8099 $BENCH_ARGS"]
