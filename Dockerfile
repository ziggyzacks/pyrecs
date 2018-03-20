FROM gcr.io/pyrecs-198313/base:latest

ENV HOME /usr/src/pyrecs
ENV OPENBLAS_NUM_THREADS 1

RUN pip install awscli \
                boto3 \
                gcloud \
                ipython \
                sanic_jinja2 \
                sanic_session

WORKDIR ${HOME}
COPY . .

EXPOSE 8000

CMD mkdir data
CMD gsuitl cp -r gs://pyrecs-198313.appspot.com/data/ data/
CMD /bin/ash -c "redis-server --daemonize yes && python app.py"
