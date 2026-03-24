variable "cloudflare_zone_id" {
  description = "Cloudflare zone ID for brandoncamenisch.com."
  type        = string
  sensitive   = true
}

variable "blog_subdomain" {
  description = "Subdomain name for the blog DNS record."
  type        = string
  default     = "blog"
}

variable "blog_target" {
  description = "GitHub Pages host target for the blog subdomain."
  type        = string
  default     = "brandoncamenisch.github.io"
}

variable "proxied" {
  description = "Whether Cloudflare should proxy the blog DNS record."
  type        = bool
  default     = false
}
