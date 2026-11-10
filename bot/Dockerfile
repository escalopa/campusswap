FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml README.md ./
COPY campusswap_bot ./campusswap_bot
RUN pip install --no-cache-dir ".[cloud]"
COPY deploy/config.cloud.toml ./config.cloud.toml
USER nobody
CMD ["python", "-m", "campusswap_bot.server", "--config", "config.cloud.toml"]
