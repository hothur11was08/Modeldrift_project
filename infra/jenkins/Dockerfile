FROM jenkins/jenkins:lts-jdk11

USER root

# Install Docker CLI
RUN apt-get update && \
    apt-get install -y docker.io curl && \
    rm -rf /var/lib/apt/lists/*

# Install Docker Compose v2 manually
RUN curl -SL https://github.com/docker/compose/releases/download/v2.30.3/docker-compose-linux-$(dpkg --print-architecture) \
    -o /usr/local/bin/docker-compose && \
    chmod +x /usr/local/bin/docker-compose

USER jenkins

