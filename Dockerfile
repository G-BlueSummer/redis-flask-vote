FROM python:3-alpine

WORKDIR /code

RUN apk add --no-cache gcc musl-dev linux-headers

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt && pip install gunicorn

COPY . .

CMD ["gunicorn", "-b", "0.0.0.0:5000", "vote:app"]