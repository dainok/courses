Build with:

```
docker build -t dainok/grficsv2-workstation:latest .
```

Run with:

```
docker run --name workstation --rm -d -p 443:6901 --shm-size=512m -e VNC_PW=password dainok/grficsv2-workstation:latest
```

Login with `kasm_user` and the password above.

Publish with:

```
docker login --username=dainok
docker push dainok/grficsv2-workstation:latest
```
