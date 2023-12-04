FROM python:3.9
# actually python image is debian based

ENV DEBIAN_FRONTEND noninteractive

RUN pip install --upgrade pip

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt update -y && apt install libgl1-mesa-glx sudo chromium chromium-driver -y


WORKDIR /usr/src/telegram_bot

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY . .
ENV PYTHONPATH=/usr/src

CMD ["python3", "./main.py"]
