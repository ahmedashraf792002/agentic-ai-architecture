resource "aws_instance" "payment_service" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.medium"
  tags = {
    Name = "payment-service-node"
  }
}

resource "aws_db_instance" "payment_db" {
  engine         = "postgres"
  instance_class = "db.t3.small"
  allocated_storage = 20
}
