FROM jupyter/datascience-notebook

ADD requirements.txt .

USER root
RUN apt update && \
    apt install -y --no-install-recommends \
    nodejs time fortune fortunes \
    openjdk-8-jre curl jq vim

# Spark dependencies
# Default values can be overridden at build time
# (ARGS are in lower case to distinguish them from ENV)
ARG spark_version="3.1.1"
ARG hadoop_version="3.2"
ARG spark_checksum="E90B31E58F6D95A42900BA4D288261D71F6C19FA39C1CB71862B792D1B5564941A320227F6AB0E09D946F16B8C1969ED2DEA2A369EC8F9D2D7099189234DE1BE"
ARG openjdk_version="11"

ENV APACHE_SPARK_VERSION="${spark_version}" \
    HADOOP_VERSION="${hadoop_version}"

RUN mkdir -p /usr/share/man/man1 \
    && apt update \
    && apt install -y --no-install-recommends wget openjdk-11-jre-headless ca-certificates-java \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Spark installation
WORKDIR /tmp
RUN wget --progress=dot:giga "https://archive.apache.org/dist/spark/spark-${APACHE_SPARK_VERSION}/spark-${APACHE_SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz" \
    && echo "${spark_checksum} *spark-${APACHE_SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz" | sha512sum -c - \
    && tar xzf "spark-${APACHE_SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz" -C /usr/local --owner root --group root --no-same-owner \
    && rm "spark-${APACHE_SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz" \
    && mv -v "/usr/local/spark-${APACHE_SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}" /usr/local/spark

WORKDIR /usr/local

# Configure Spark
ENV SPARK_HOME=/usr/local/spark
ENV SPARK_OPTS="--driver-java-options=-Xms1024M --driver-java-options=-Xmx4096M --driver-java-options=-Dlog4j.logLevel=info" \
    PATH=$PATH:$SPARK_HOME/bin
WORKDIR /code

ADD requirements.txt .
USER jovyan

RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install --no-cache-dir --upgrade -r requirements.txt

ENV PYTHONPATH=$SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-0.10.9-src.zip:$PYTHONPATH