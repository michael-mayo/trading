
```commandline
cd ~/trading
docker compose build && docker run -v $PWD/src:/app -v $PWD/data:/data -it trading:latest
```
then run programs from the `app` directory.