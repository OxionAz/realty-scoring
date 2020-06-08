FROM python:3.8-slim

ARG PROJECT_NAME

COPY . /$PROJECT_NAME
WORKDIR /$PROJECT_NAME/

RUN pip install -U -r requirements.txt

ENTRYPOINT ["./run.sh"]