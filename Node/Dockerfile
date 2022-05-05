
FROM python:3.7
COPY . .
# ADD . /app
# WORKDIR /app
RUN pip install -r requirements.txt
# RUN pip install -r requirements.txt
# ENV FLASK_APP=server.py
# ENV PORT=5000
EXPOSE 5555

ENTRYPOINT ["python", "-u", "app.py"]
# FROM python:3.7
# ADD . /app
# WORKDIR /app
# RUN pip install -r requirements.txt
# # ENV FLASK_APP=server.py
# ENV PORT=5000
# EXPOSE 5555

# ENTRYPOINT [ "python" ]

# CMD [ "app.py" ]