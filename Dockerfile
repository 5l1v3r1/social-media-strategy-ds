FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

COPY ./app /app

RUN apt-get update
RUN apt-get install -qy python3

WORKDIR /app

# Come back and make this and installation of requirements.txt
RUN pip install tweepy python-dotenv fastapi pandas uvicorn

ENV TIMEOUT=36000

ENV GRACEFUL_TIMEOUT=36000

COPY ./app /app

EXPOSE 80

# Used to test locally
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]