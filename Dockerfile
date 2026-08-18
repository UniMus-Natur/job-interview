# Multi-stage build. The runtime image carries only the source and the data it
# needs — no build tooling, no test files.
FROM python:3.12-slim AS build
WORKDIR /build
COPY pyproject.toml README.md ./
COPY src/ ./src/
RUN python -m pip install --no-cache-dir --upgrade pip build \
 && python -m build --wheel --outdir /dist

FROM python:3.12-slim AS runtime
LABEL org.opencontainers.image.title="dwc-etl" \
      org.opencontainers.image.description="Raw species observations to Darwin Core occurrences"
WORKDIR /app

# Run unprivileged; the mounted output directory is owned by this user.
RUN useradd --create-home --uid 1000 etl
COPY --from=build /dist/*.whl /tmp/
RUN python -m pip install --no-cache-dir /tmp/*.whl && rm /tmp/*.whl

COPY data/ ./data/
RUN mkdir -p output && chown -R etl:etl /app
USER etl

# Overridable: docker run ... dwc-etl --database data/other.db --output output/x.csv
ENTRYPOINT ["python", "-m", "dwc_etl"]
CMD ["--verbose"]
