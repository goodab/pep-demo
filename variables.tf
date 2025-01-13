variable "aws_region" {
  description = "AWS region for all resources."

  type    = string
  default = "us-west-2"
}

variable "aws_data_bucket_name" {
    type = string
    default = "pep-site-datafeed"
}

variable "num_sites" {
    type = number
    default = 5
}

variable "upload_interval_minutes" {
  type=number
  default = 5
}

variable "max_gen_energy_kwh" {
  type=number
  default = 1000
}

variable "min_gen_energy_kwh" {
  type=number
  default = -100
}

variable "max_consumed_energy_kwh" {
  type=number
  default = 1000
}

variable "min_consumed_energy_kwh" {
  type=number
  default = -100
}

variable "table_name" {
  type=string
  default = "EnergyData"
}