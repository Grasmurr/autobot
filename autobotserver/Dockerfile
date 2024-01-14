FROM python:3.10.5

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN apt-get update && apt-get install -y postgresql-client
RUN pip install gunicorn
RUN pip install psycopg2-binary
RUN pip install -r requirements.txt

COPY . .

ENV DJANGO_SETTINGS_MODULE=autobotserver.settings
ENV PYTHONUNBUFFERED=1

CMD ["gunicorn", "autobotserver.wsgi:application", "--bind", "0.0.0.0:8000"]
