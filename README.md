# pyrecs
rex w/python


## Development
```bash
# current docker image
docker run -p 8000:8000 gcr.io/pyrecs-198313/api
```

```bash
# building, tagging, & pushing
docker build -t pyrecs/api .
docker tag pyrecs/api gcr.io/pyrecs-198313/api
gcloud docker -- push gcr.io/pyrecs-198313/api
```

### Deploys
```bash
gcloud beta compute instances update-container pyrecs-api --container-image gcr.io/pyrecs-198313/api
```