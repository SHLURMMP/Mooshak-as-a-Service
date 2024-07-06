variable "KeyPair" {
  type = string
  default = "Concurso"
}

variable "ContestTitle" {
  type = string
  default = "Concurso"
}

variable "ContestDescription" {
  type = string
  default = "Concurso"
}

variable "ContestInstanceType" {
  type = string
  default = "t2.micro"
}

provider "aws" {
    region = "eu-west-1"
    shared_credentials_files = ["/home/pedro/.aws/credentials"]
    profile = "default"
}

resource "aws_instance" "my_instance" {
    ami           = "ami-0d940f23d527c3ab1"
    instance_type = var.ContestInstanceType
    key_name = var.KeyPair
    vpc_security_group_ids = [ "sg-03f4cbf2c45c9dd6c" ]

    tags = {
        Name = var.ContestTitle
        Description = var.ContestDescription
    }
}

