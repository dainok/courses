Build with:

```
docker build -t dainok/grficsv2-ews:latest .
```

Run with:

```
docker run --name ews --rm -d -p 443:6901 --privileged --shm-size=512m -e VNC_PW=password dainok/grficsv2-ews:latest
```

Login with `kasm_user` and the password above.

Eventually map a local volume:

```
docker run --name ews --rm -d -p 443:6901 --privileged --shm-size=512m -v /tmp:/home/kasm-user/Downloads -e VNC_PW=password dainok/grficsv2-ews:latest
```

You can run everything in a box:

```
docker run --name simulation --rm -d -p 8380:80 -p 5020:5020 -p 5021:5021 -p 5022:5022 -p 5023:5023 -p 5024:5024 -p 5025:5025 dainok/grficsv2-simulation:latest
docker run --name plc --rm -d -p 502:502 -p 8280:8080 -e SIM=172.24.9.183 dainok/grficsv2-plc:latest
docker run --name hmi --rm -d -p 8180:8080 dainok/grficsv2-hmi:latest
docker run --name ews --rm -d -p 443:6901 --privileged --shm-size=512m -e VNC_PW=password dainok/grficsv2-ews:latest
```

Publish with:

```
docker login --username=dainok
docker push dainok/ews:latest
```
