Build with:

```
docker build -t dainok/virtuaplant-bottle-filling-plc:latest .
```

Run with:

```
docker run --name plc --rm -d -p 443:6901 -p 502:5020 -e VNC_PW=password dainok/virtuaplant-bottle-filling-plc:latest
```

Login with `kasm_user` and the password above.

Publish with:

```
docker login --username=dainok
docker push dainok/virtuaplant-bottle-filling-plc:latest
```
