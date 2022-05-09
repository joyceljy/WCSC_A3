FROM python:3.8
WORKDIR /shortener
COPY shortener .
RUN pip install flask gunicorn gevent Flask-SQLAlchemy PyJWT requests
ENV LISTEN_PORT=5000
EXPOSE 5000
CMD gunicorn -b 0.0.0.0:5000 -w 2 wscs:app