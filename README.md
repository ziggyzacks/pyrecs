# pyrecs
rex w/python


## API
```bash
curl http://pyrecs.com/api/similar?movies=<int>
curl http://pyrecs.com/api/metadata?movies=<int>
```

## Development

```bash
docker build -t pyrecs/api .
docker tag pyrecs/api gcr.io/pyrecs-198313/api
gcloud docker -- push gcr.io/pyrecs-198313/api
```

### Deploys
```bash
gcloud beta compute instances update-container pyrecs-api --container-image gcr.io/pyrecs-198313/api
```