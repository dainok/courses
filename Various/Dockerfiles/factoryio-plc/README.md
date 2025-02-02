Build with:

```
docker build -t dainok/grficsv2-plc:latest .
```

Run with:

```
docker run --name plc --rm -d -p 502:502 -p 80:8080 -e SIM=192.168.1.1 dainok/grficsv2-plc:latest
```

Login with `openplc` and the password `openplc`.

Publish with:

```
docker login --username=dainok
docker push dainok/grficsv2-plc:latest
```
