Build with:

```
docker build -t dainok/virtuaplant-oil-refinery-hmi:latest .
```

Run with:

```
docker run --name hmi --rm -d -p 443:6901 -e PLC=192.168.1.1 -e VNC_PW=password dainok/virtuaplant-oil-refinery-hmi:latest
```

Login with `kasm_user` and the password above.

Publish with:

```
docker login --username=dainok
docker push dainok/virtuaplant-oil-refinery-hmi:latest
```
