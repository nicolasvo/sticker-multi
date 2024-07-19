FROM python:3.12-slim

WORKDIR /app

RUN apt update && apt install -y libgl1-mesa-glx libglib2.0-0
COPY requirements.txt /app/
COPY bot.py sticker.py user.py /app/

RUN pip install -r requirements.txt

ENTRYPOINT ["python"]
CMD ["bot.py"]
