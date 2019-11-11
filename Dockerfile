FROM python:3.6

MAINTAINER vinh-ngu@hotmail.com

WORKDIR /app
ADD . .
RUN pip install -r requirements.txt

CMD ["python", "main.py"]
