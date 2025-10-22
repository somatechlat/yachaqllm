FROM python:3.11-slim

WORKDIR /app

# Install system deps required to build native wheels and run headless Chromium
RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
	   git \
	   build-essential \
	   ca-certificates \
	   wget \
	   curl \
	   gnupg \
	   fonts-liberation \
	   libnss3 \
	   libatk1.0-0 \
	   libx11-6 \
	   libxcomposite1 \
	   libxdamage1 \
	   libxrandr2 \
	   libgtk-3-0 \
	   libasound2 \
	   libxss1 \
	   libgbm1 \
	&& rm -rf /var/lib/apt/lists/*

# Install chromium
RUN apt-get update && apt-get install -y --no-install-recommends chromium && rm -rf /var/lib/apt/lists/*
ENV CHROME_PATH=/usr/bin/chromium

# Copy application files
COPY requirements.txt .
COPY . .

# Install Python dependencies (including git+ packages)
RUN python -m pip install --upgrade pip setuptools wheel && python -m pip install -r requirements.txt

EXPOSE 8000
ENV PORT=8000
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
