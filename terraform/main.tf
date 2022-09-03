terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~>3.27"
    }
  }

  required_version = ">=0.14.9"

  backend "s3" {
    bucket = "tfconfigbucket"
    key    = "messenger.tfstate"
    region = "eu-west-1"
  }
}

data "aws_availability_zones" "azs" {}

provider "aws" {
  region = "eu-west-1"
}

resource "aws_vpc" "vpc" {
  cidr_block           = "10.0.0.0/22"
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = {
    Name = "Terraform VPC"
  }
}

resource "aws_internet_gateway" "internet_gateway" {
  vpc_id = aws_vpc.vpc.id
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.internet_gateway.id
  }
}

resource "aws_route_table_association" "route_table_association" {
  count = var.availability_zones_count

  subnet_id      = aws_subnet.pub_subnet.*.id[count.index]
  route_table_id = aws_route_table.public.id
}


resource "aws_ecr_repository" "messenger_service" {
  name = "messenger-service"
}

output "alb-dns-name" {
  value = aws_alb.alb.dns_name
}
