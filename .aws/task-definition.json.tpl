[{
    "essential": true,
    "memory": 512,
    "name": "${SERVICE_NAME}",
    "cpu": 2,
    "image": "${REPOSITORY_URL}",
    "environment": [],
    "portMappings": [{
        "containerPort": ${SERVICE_PORT},
        "hostport": ${SERVICE_PORT}
    }]
}]
