FROM gcr.io/pyrecs-198313/base:latest

ENV HOME /usr/src/pyrecs
ENV OPENBLAS_NUM_THREADS 1

RUN pip install awscli \
                boto3 \
                gcloud \
                ipython \
                sanic_jinja2 \
                sanic_session

RUN apk update && apk add nginx

WORKDIR ${HOME}
COPY . .

EXPOSE 80

CMD mkdir data logs
CMD gsuitl cp -r gs://pyrecs-198313.appspot.com/data/ data/
CMD /bin/ash -c "redis-server --daemonize yes && \
                 nginx -p ${HOME} -c nginx/nginx.conf && \
                 python app.py"
