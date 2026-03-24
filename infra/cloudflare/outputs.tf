output "blog_fqdn" {
  description = "Fully qualified blog hostname."
  value       = local.blog_fqdn
}

output "blog_target" {
  description = "GitHub Pages target hostname."
  value       = cloudflare_record.blog_pages.hostname
}
