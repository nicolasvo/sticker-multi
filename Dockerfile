FROM python:3.10

WORKDIR /app

RUN apt update && apt install -y libgl1-mesa-glx
COPY requirements.txt .
COPY bot.py sticker.py user.py .

RUN pip install -r requirements.txt

ENTRYPOINT ["python"]
CMD ["bot.py"]
