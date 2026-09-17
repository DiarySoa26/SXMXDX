FROM apache/spark:4.0.1-python3

USER root

RUN mkdir -p /opt/spark/jars

ADD https://jdbc.postgresql.org/download/postgresql-42.7.7.jar \
    /opt/spark/jars/postgresql.jar

RUN chmod 644 \
    /opt/spark/jars/postgresql.jar

WORKDIR /app

USER spark