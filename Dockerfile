FROM python:3.10.11-slim

ENV BOT_HOME=bot

WORKDIR $BOT_HOME

COPY . .

RUN pip install poetry
RUN poetry config virtualenvs.create false && poetry install --only main

EXPOSE 5000

CMD ["python", "bot_v5.py"]