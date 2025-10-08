# URL or IP (e.g., https://10.10.10.10)
variable "url" {
  description = "URL or IP address"
  type        = string
}

# Username for authentication
variable "username" {
  description = "Username for login"
  type        = string
  sensitive   = true
}

# Password for authentication
variable "password" {
  description = "Password for login"
  type        = string
  sensitive   = true
}

# Whether to ignore TLS certificate validation (true = skip validation)
variable "insecure" {
  description = "Ignore TLS certificate validation"
  type        = bool
  default     = true
}
