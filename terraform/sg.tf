resource "aws_security_group" "public_sg" {
  name        = "public-group-default"
  description = "access to public instances"
  vpc_id      = aws_vpc.vpc.id
}

resource "aws_security_group" "alb_sg" {
  name        = "alb-sg"
  description = "control access to the app load balancer"
  vpc_id      = aws_vpc.vpc.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "ecs_sg" {
  name        = "esc-from-alb-group"
  description = "control access to the cluster"
  vpc_id      = aws_vpc.vpc.id

  ingress {
    from_port       = var.messenger_port
    to_port         = var.messenger_port
    protocol        = "tcp"
    cidr_blocks     = ["0.0.0.0/0"]
    security_groups = [aws_security_group.alb_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
