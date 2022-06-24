FROM jupyter/datascience-notebook

WORKDIR /code

USER root

# Next the java dependency is not likely to change often
ARG openjdk_version="17"
RUN mkdir -p /usr/share/man/man1 \
    && apt update \
    && apt install -y --no-install-recommends \
        wget "openjdk-${openjdk_version}-jre-headless" ca-certificates-java jq \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Spark dependencies
# Default values can be overridden at build time
# (ARGS are in lower case to distinguish them from ENV)
ENV APACHE_SPARK_VERSION="3.3.0"
ENV HADOOP_VERSION="3"

ARG install_root=/usr/local

ENV SPARK_HOME=${install_root}/spark
ENV PATH=$PATH:$SPARK_HOME/bin
ENV SPARK_OPTS="--driver-java-options=-Xms1024M --driver-java-options=-Xmx4096M --driver-java-options=-Dlog4j.logLevel=info"
ENV PYTHONPATH=$SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-0.10.9-src.zip:$PYTHONPATH

# Finally, install spark & hadoop
WORKDIR /tmp
RUN wget --progress=dot:giga "https://archive.apache.org/dist/spark/spark-${APACHE_SPARK_VERSION}/spark-${APACHE_SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz" \
    && spark_checksum=$(wget -O - "https://archive.apache.org/dist/spark/spark-${APACHE_SPARK_VERSION}/spark-${APACHE_SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz.sha512" | cut -d' ' -f1) \
    && echo "${spark_checksum} *spark-${APACHE_SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz" | sha512sum -c - \
    && tar xzf "spark-${APACHE_SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz" -C "${install_root}" --owner root --group root --no-same-owner \
    && rm "spark-${APACHE_SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz" \
    && mv -v "${install_root}/spark-${APACHE_SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}" "${install_root}/spark"

WORKDIR /code

USER jovyan
ADD requirements.txt .
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install --no-cache-dir --upgrade -r requirements.txt

