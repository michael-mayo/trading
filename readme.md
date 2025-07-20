
```commandline
cd ~/trading
docker compose build && docker run -v $PWD/src:/app -it trading:latest
```