# pyrecs
rex w/python


## API
```bash
❱ time curl 'http://pyrecs.com/api/metadata?movies=1' | jq                                                                                                                                                               +14734 18:08 ❰─┘
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   111  100   111    0     0   1544      0 --:--:-- --:--:-- --:--:--  1608
{
  "movies": [
    {
      "title": "Toy Story",
      "year": 1995,
      "genres": [
        "Adventure",
        "Animation",
        "Children",
        "Comedy",
        "Fantasy"
      ]
    }
  ]
}
curl 'http://pyrecs.com/api/metadata?movies=1'  0.00s user 0.00s system 10% cpu 0.080 total
jq  0.00s user 0.00s system 5% cpu 0.080 total
```

```bash
❱ time curl 'http://pyrecs.com/api/similar?movies=1&n=5' | jq                                                                                                                                                            +14735 18:09 ❰─┘
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   586  100   586    0     0   8234      0 --:--:-- --:--:-- --:--:--  8492
{
  "1": {
    "metadata": {
      "title": "Toy Story",
      "year": 1995,
      "genres": [
        "Adventure",
        "Animation",
        "Children",
        "Comedy",
        "Fantasy"
      ]
    },
    "similar": [
      {
        "title": "Aladdin",
        "year": 1992,
        "genres": [
          "Adventure",
          "Animation",
          "Children",
          "Comedy",
          "Musical"
        ]
      },
      {
        "title": "Come See the Paradise",
        "year": 1990,
        "genres": [
          "Drama",
          "Romance"
        ]
      },
      {
        "title": "Babe",
        "year": 1995,
        "genres": [
          "Children",
          "Drama"
        ]
      },
      {
        "title": "Lion King, The",
        "year": 1994,
        "genres": [
          "Adventure",
          "Animation",
          "Children",
          "Drama",
          "Musical",
          "IMAX"
        ]
      },
      {
        "title": "Beauty and the Beast",
        "year": 1991,
        "genres": [
          "Animation",
          "Children",
          "Fantasy",
          "Musical",
          "Romance",
          "IMAX"
        ]
      }
    ]
  }
}
curl 'http://pyrecs.com/api/similar?movies=1&n=5'  0.00s user 0.00s system 10% cpu 0.080 total
jq  0.00s user 0.00s system 7% cpu 0.080 total
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