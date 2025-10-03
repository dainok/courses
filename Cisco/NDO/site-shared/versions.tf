terraform {
  required_version = ">= 1.8.0"

  required_providers {
    mso = {
      source  = "CiscoDevNet/mso"
      version = ">= 1.5.1"
    }
    utils = {
      source  = "netascode/utils"
      version = ">= 1.0.2"
    }
    local = {
      source  = "hashicorp/local"
      version = ">= 2.3.0"
    }
  }
}