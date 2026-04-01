variable "cloudflare_zone_id" {
  description = "Cloudflare zone ID for brandoncamenisch.com."
  type        = string
  sensitive   = true
}

variable "blog_target" {
  description = "GitHub Pages host target for the apex domain DNS record."
  type        = string
  default     = "brandoncamenisch.github.io"
}

variable "proxied" {
  description = "Whether Cloudflare should proxy the DNS record. Must be true for CNAME flattening at the apex."
  type        = bool
  default     = true
}
