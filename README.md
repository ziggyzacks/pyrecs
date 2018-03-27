# pyrecs
rex w/python


## API
```bash
❱ curl 'http://pyrecs.com/api/metadata?movies=1' | jq                                                                                                                                                               +14734 18:08 ❰─┘
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
```

```bash
❱ curl 'http://pyrecs.com/api/similar?movies=1&n=5' | jq                                                                                                                                                            +14735 18:09 ❰─┘
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