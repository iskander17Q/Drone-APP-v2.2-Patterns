FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

COPY DesignPatterns_V3/monolith/requirements.txt requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

ENV FLASK_APP=DesignPatterns_V3/monolith/manage.py

CMD ["flask", "--app", "DesignPatterns_V3/monolith/manage.py", "run", "--host=0.0.0.0", "--port=5000"]

