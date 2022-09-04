resource "aws_ecs_cluster" "ecs_cluster" {
  name = "test-cluster"
}

data "template_file" "task_definition_template" {
  template = file("../.aws/task-definition.json.tpl")
  vars = {
    REPOSITORY_URL = replace(aws_ecr_repository.messenger_service.repository_url, "https://", "")
    SERVICE_NAME = var.service_name
    SERVICE_PORT = var.service_port
  }
}

resource "aws_ecs_task_definition" "task_definition" {
  family                   = "messenger-service"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 256
  memory                   = 512
  container_definitions    = data.template_file.task_definition_template.rendered
  execution_role_arn       = aws_iam_role.ecs_task.arn
}

resource "aws_ecs_service" "messenger_service" {
  name            = "messenger-service"
  cluster         = aws_ecs_cluster.ecs_cluster.id
  task_definition = aws_ecs_task_definition.task_definition.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    security_groups  = [aws_security_group.ecs_sg.id]
    subnets          = aws_subnet.pub_subnet.*.id
    assign_public_ip = true
  }

  load_balancer {
    container_name   = "messenger-service"
    container_port   = var.service_port
    target_group_arn = aws_alb_target_group.target_group.id
  }

  depends_on = [
    aws_alb_listener.alb_listener
  ]
}
