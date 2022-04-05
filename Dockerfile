FROM python:3.6
ADD . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENV FLASK_APP=server.py
# EXPOSE 5100
CMD [ "python3", "server.py"]
