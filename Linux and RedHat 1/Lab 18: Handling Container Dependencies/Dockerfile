FROM docker.io/library/python:3.9-alpine
WORKDIR /app

COPY entrypoint.sh .
COPY healthcheck.sh .
COPY app.py .

RUN chmod +x entrypoint.sh healthcheck.sh \
    && pip install psycopg2-binary

ENTRYPOINT ["./entrypoint.sh"]
CMD ["python", "app.py"]
