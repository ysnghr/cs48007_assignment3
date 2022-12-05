# CS48007 YOLO Model Server side


## Usage

Firstly, build the docker file with following command.

```bash
sudo docker build -t yolo5-flask .  
```

Then run it with this command on port 80.

```bash
sudo docker run --rm -it --network=host -p 80:80 yolo5-flask
```