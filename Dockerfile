FROM python:3.10

WORKDIR /app
COPY requirements.txt .
COPY bot.py sticker.py user.py .

RUN pip install -r requirements.txt

ENTRYPOINT ["python"]
CMD ["bot.py"]
