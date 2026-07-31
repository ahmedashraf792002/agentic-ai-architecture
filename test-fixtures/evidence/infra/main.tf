# Order Platform infrastructure (fixture, deliberately minimal Terraform)

resource "aws_db_instance" "payment_database" {
  identifier     = "payment-database"
  engine         = "postgres"
  instance_class = "db.t3.medium"
  # Node: Payment Database — hosts payment_authorizations table
  # (see code/schema.sql). Isolated per constraint C1 / principle P1
  # in motivation/strategic-goals.md.
}

resource "aws_instance" "order_api_server" {
  ami           = "ami-fixture0000000"
  instance_type = "t3.medium"
  tags = {
    Name = "order-api-server"
  }
  # Node: Order API Server — hosts the OrderService application component
  # (see code/order-service/main.py).
}

resource "aws_instance" "payment_api_server" {
  ami           = "ami-fixture0000001"
  instance_type = "t3.medium"
  tags = {
    Name = "payment-api-server"
  }
  # Node: Payment API Server — hosts the PaymentService application
  # component (see code/payment-service/main.py). Deployed separately
  # from order-api-server per the isolation principle (P1).
}

# System Software running on both nodes
resource "aws_ssm_document" "runtime_config" {
  name = "python-3-11-runtime"
  # System Software: Python 3.11 Runtime
}
