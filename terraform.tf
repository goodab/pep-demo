terraform {

  cloud {
    workspaces {
      name = "pep-demo"
    }
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.38.0"
    }
  }

  required_version = "~> 1.2"
}

provider "aws" {
  region = var.aws_region
}
