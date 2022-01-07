FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

ENV PORT 8000

EXPOSE 8000

RUN rm -rf /app/*

COPY . /app

WORKDIR /app

ARG USER_ID=1000
RUN groupadd bgd && \
    adduser --disabled-password --gecos "" --uid ${USER_ID} --ingroup bgd bgd && \
    chown -R bgd:bgd /app

RUN chmod a+x start.sh

RUN pip install --no-cache-dir --upgrade -r requirements.txt

USER bgd

CMD ["./start.sh"]
