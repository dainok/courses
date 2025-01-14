Build with:

```
docker build -t dainok/virtuaplant-bottle-filling-hmi:latest .
```

Run with:

```
docker run --name hmi --rm -d -p 443:6901 -e PLC=192.168.1.1 dainok/virtuaplant-bottle-filling-hmi:latest
```

Publish with:

```
docker login --username=dainok
docker push dainok/virtuaplant-bottle-filling-hmi:latest
```
