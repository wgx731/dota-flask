# Grab base image
FROM python:3.6.2-alpine3.6

# Copy requirements
COPY ./requirements.txt /tmp/requirements.txt

# Install dependencies
RUN apk add --no-cache --virtual .build-deps \
    postgresql-dev \
    gcc \
    musl-dev \
    && pip3 install --no-cache-dir -q -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt

# Add our code
COPY app /opt/webapp/app
COPY wsgi.py /opt/webapp/
COPY create_db.py /opt/webapp/
COPY drop_db.py /opt/webapp/
WORKDIR /opt/webapp

# Run the image as a non-root user
RUN adduser -D flaskuser
USER flaskuser

# Run the app.  CMD is required to run on Heroku
# $PORT is set by Heroku
CMD gunicorn --bind 0.0.0.0:$PORT --access-logfile - wsgi

