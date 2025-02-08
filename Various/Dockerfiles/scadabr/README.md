Build with:

```
docker build -t dainok/scadabr:latest .
```

Run with:

```
docker run --name hmi -d -p 80:8080 dainok/scadabr:latest
```

Publish with:

```
docker login --username=dainok
docker push dainok/scadabr:latest
```
