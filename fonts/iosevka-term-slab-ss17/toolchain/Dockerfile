FROM node:22-bookworm-slim

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y \
        ttfautohint \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /work/iosevka
