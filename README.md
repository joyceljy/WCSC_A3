# Assignment 3: Virtualization using Docker
## Introduction
The main goal of this assignment is to containerize the URL shortening project from the previous assignment using Docker technology in order to more efficiently allocate and isolate resource usages.

## Install 
Install Kubernetes and Docker on your virtual machine beforehand.
### 3.1
Step1：Build the auth server image.
```console
docker build -t auth .
```
Step2: Run the container of auth server.
```console
docker run -it --name flask_container2 -p 5001:5001 shortener
```

Step3: Build the shortener server image.
```console
docker build -t shortener .
```

Step4: Run the container of shortener server and link it to the auth server(start auth server first)
```console
docker run -it --name flask_container3 --link flask_container2:auth_server -p 5000:5000 shortener
```

### 3.2
Step1: Upload the code of shortener to the work nodes.
```console
scp -r /Users/aaa/Downloads/wdsc/A3.1/shortener student030@145.100.134.30:/home/student030
```

Step2: Building the shortener image on server.
```console
docker build -t shortener .
```

Step3: Upload the code of shortener to the work nodes.
```console
scp -r /Users/aaa/Downloads/wdsc/A3.1/auth student028@145.100.134.28:/home/student028
```

Step4: Building the auth image on server.
```console
docker build -t auth .
```

Step5: Upload the yaml files to the master node.
```console
scp -r /Users/aaa/Downloads/wdsc/A3.1/auth.yaml student029@145.100.134.28:/home/student029
scp -r /Users/aaa/Downloads/wdsc/A3.1/shortener.yaml student029@145.100.134.28:/home/student029
```

Step6: Apply the deployment and service yaml files.
```console
kubectl apply -f auth.yaml
kubectl apply -f shortener.yaml
```

## Description
### Nodes
There's two nodes in our project, one master node and one worker node.
<img src="Archive/pic/nodes.png">

### Images
We used the meinheld-gunicorn image to containerize our python code. This image is avaliable on DockerHub. https://hub.docker.com/r/tiangolo/meinheld-gunicorn

### Deployments
Two deployments were created, namely shortener-deployment and auth-deployment.
<img src="Archive/pic/deployments.png">

1. shortener-deployment is used to define the behaviour of pods working for the CRUD(create, read, update and delete) of URLs. In the spec section, the replica is set as 3 which means three instance of pods will automatically create during runtime(See the red frame in the pic). The matchLabels is set as 'shortener' which means all pods that matches this label will be regulated by this deployment. The labels in the template section is set as app:shortener which means the pods created from this deployment file will have the label:shortener.(See the blue frame in the pic)

2. auth-deployment is used to define the behaviour of pods working for user login and registration. In the spec section, the replica is set as 1 (See the red frame in the pic), which means only one pods is created. The matchLabels and labels is set as 'auth'. (See the blue frame in the pic)
<img src="Archive/pic/pods.png">


### Services
Also, two services were created, namely shortener-service and auth-service.(See the red frame in the pic)

We chose nodeType as our service type. The nodePort is set as 31000 and 31001, respectively, while the port and targetPort is set as 5000 and 5001. For the selector, 'shortener' is set for shortener-service and 'auth' is set for auth-service to identify the target pods and their IP addresses. (See the blue frame in the pic)
<img src="Archive/pic/services.png">