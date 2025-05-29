ARG VARIANT=3.12-bookworm
FROM mcr.microsoft.com/devcontainers/python:${VARIANT}

ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID
ARG VESPA_CLI_VERSION=8.507.34

ENV VESPA_CLI_VERSION=${VESPA_CLI_VERSION}
ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Tokyo


WORKDIR /workspace

# Vespa CLI のインストール
RUN mkdir -p .bin && \
    curl -L -o .bin/vespa-cli.tar.gz "https://github.com/vespa-engine/vespa/releases/download/v${VESPA_CLI_VERSION}/vespa-cli_${VESPA_CLI_VERSION}_linux_arm64.tar.gz" && \
    tar -xzvf .bin/vespa-cli.tar.gz -C .bin && \
    mv .bin/vespa-cli_${VESPA_CLI_VERSION}_linux_arm64/bin/vespa .bin/vespa && \
    rm .bin/vespa-cli.tar.gz && \
    rm -rf .bin/vespa-cli_${VESPA_CLI_VERSION}_linux_arm64

ENV PATH="/workspace/.bin:${PATH}"

# Java (OpenJDK 17) および Maven のインストール
RUN apt-get update && \
    apt-get install -y openjdk-17-jdk maven && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# JAVA_HOME 環境変数の設定
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-arm64
ENV PATH="${JAVA_HOME}/bin:${PATH}"

USER $USERNAME