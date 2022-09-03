[{
    "essential": true,
    "memory": 512,
    "name": "worker",
    "cpu": 2,
    "image": "${REPOSITORY_URL}:latest",
    "environment": [],
    "portMappings": [{
        "containerPort": 5000,
        "hostport": 5000
    }]
}]
