FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DASH_DEBUG_MODE True

WORKDIR /app
RUN pip install --upgrade pip
COPY requierments.txt requierments.txt

RUN pip install -r requierments.txt

COPY . .


CMD [ "python3","-m" , "app"]
