locals {
  blog_fqdn = "brandoncamenisch.com"
}

resource "cloudflare_record" "blog_pages" {
  zone_id = var.cloudflare_zone_id
  name    = "@"
  content = var.blog_target
  type    = "CNAME"
  ttl     = 1
  proxied = var.proxied
}
