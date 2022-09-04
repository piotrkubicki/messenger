resource "aws_subnet" "pub_subnet" {
  count = var.availability_zones_count

  vpc_id                  = aws_vpc.vpc.id
  cidr_block              = "10.0.0.${128 * count.index}/25"
  availability_zone       = data.aws_availability_zones.azs.names[count.index]
  map_public_ip_on_launch = true
}
