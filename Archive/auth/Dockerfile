FROM python:3.8
WORKDIR /auth
COPY auth .
RUN pip install flask gunicorn gevent Flask-SQLAlchemy PyJWT requests
ENV LISTEN_PORT=5001
EXPOSE 5001
CMD gunicorn -b 0.0.0.0:5001 -w 2 auth:app