---
title: 'The top tools to know for platform work in 2026'
description: 'A practical look at the tools and skills that keep resurfacing across recursively scanned resume/work YAMLs: IaC, containers, CI/CD, observability, security, and automation languages.'
pubDate: 'Mar 26 2026'
generatedHeroImage: '/images/generated/top-tools-platform-work-2026-terminal-banner.jpg'
generatedImages:
  - id: stack-review-desk
    alt: 'AI-generated platform engineering desk with cloud diagrams, observability screens, and deployment workflow cues.'
    caption: 'Tool depth matters more than tool collecting: a smaller stack you can operate well beats a long list you only recognize by name.'
    brief: 'Create a supporting in-article image for a post about the top tools to know for platform engineering in 2026: practical Linux desk, architecture notes, observability screens, deployment workflow cues, and a thoughtful operator perspective.'
---

I did a recursive scan through the YAML files under `/home/captain/Public/ghorg/brandoncamenisch/resume/work` to see which tools and skills kept resurfacing across platform, DevOps, SRE, and infrastructure-oriented resume variants.

[[generated-image:stack-review-desk]]

The exact counts are a little noisy because some resumes are tailored versions of the same core experience, but the pattern is still obvious. The same stack families show up again and again: infrastructure as code, containers and schedulers, CI/CD, observability, security controls, and a small set of languages used to automate all of it.

If I had to compress that scan into the top tools to know for platform work in 2026, this is where I would spend my time.

## 1. Terraform

Terraform is still one of the clearest dividing lines between “I can click through cloud setup” and “I can build repeatable infrastructure.” It shows up everywhere because platform teams need reproducibility, reviewable change, and the ability to stamp environments out consistently.

The important skill is not just writing resources. It is learning how to structure modules, manage state carefully, and keep environment differences small enough that drift does not become its own platform.

## 2. Kubernetes

Kubernetes remains one of the most reusable pieces of platform knowledge because so many adjacent tools and workflows assume you understand it. Even when teams are using managed services or simpler abstractions, the mental model of workloads, networking, config, rollout behavior, and cluster operations still pays off.

You do not need to memorize every API object. You do need to understand how applications actually get scheduled, configured, exposed, observed, and recovered when something goes wrong.

## 3. Cloud fundamentals across AWS, Azure, and GCP

The YAML scan kept surfacing multi-cloud language. In practice, that usually means AWS first, with Azure and GCP showing up often enough that ignorance is expensive.

The useful skill here is not vendor trivia. It is being able to reason about identity, networking, compute, storage, and cost in whichever cloud you land in, then map those primitives back to the platform patterns your team needs.

## 4. CI/CD systems like GitHub Actions and GitLab CI

Platform work is hard to separate from delivery workflows. GitHub Actions and GitLab CI kept showing up because they sit right in the path between code and production.

Knowing these tools means more than writing a pipeline file. It means understanding build isolation, secrets handling, promotion flow, artifact management, policy checks, and how to keep deployment paths boring enough that teams trust them.

## 5. Docker and workload packaging

Container fluency still matters because packaging is where software delivery becomes operational. If you do not understand images, layers, entrypoints, runtime assumptions, and dependency boundaries, everything further down the line gets messier.

Docker is not the whole platform job, but it is still one of the fastest ways to build intuition for how code becomes a thing that can actually run somewhere repeatably.

## 6. Observability with Prometheus, Grafana, and Datadog

The recurring observability stack in the YAML set was hard to miss. Prometheus, Grafana, and Datadog appear because platform teams are expected to know not only whether a service is up, but whether the platform itself is healthy, efficient, and trusted.

That means knowing how to think in signals: metrics, logs, traces, alert quality, dashboards, SLOs, and feedback loops that help teams notice problems before they become incidents.

## 7. Security controls like Vault, IAM, and secrets management

Security kept showing up not as a separate specialty, but as part of the normal operating model. Vault, IAM hardening, policy enforcement, and secret handling are all core platform concerns now.

That is a healthy shift. In 2026, good platform work is not just about speed. It is about making the safe path the default path without turning every release into a ceremony.

## 8. Automation languages: Go, Python, and Bash

The language pattern in the YAMLs is also consistent. Go and Python come up constantly, with Bash still hanging around because platform teams live close to operating systems, build scripts, and glue code.

If I were choosing where to invest, I would learn enough Go to build reliable tooling and services, enough Python to move quickly in automation and data-shaped workflows, and enough shell to debug and compose systems without fear.

## 9. Configuration and orchestration tools like Ansible, ArgoCD, Nomad, ECS, and Fargate

One of the clearest lessons from the scan is that platform work is rarely a single-tool job. Even if Kubernetes is central, teams still keep running into surrounding systems for configuration management, GitOps delivery, or workload scheduling.

That is why tools like Ansible, ArgoCD, Nomad, ECS, and Fargate still matter. You may not use all of them in one role, but seeing how they fit into the broader operating model makes you much more adaptable.

## 10. The skill underneath the tools: systems judgment

This is the part that matters most. The recursive scan is useful because it highlights the repeated nouns, but the real signal is what those tools are doing together.

They are all in service of the same outcomes:

- repeatable infrastructure
- safer delivery
- clearer observability
- better security defaults
- lower cognitive load for the people building products

So yes, learn Terraform, Kubernetes, GitHub Actions, Docker, Prometheus, Vault, Go, and Python. But do it with an eye toward how they connect. Platform engineering gets better when you stop treating tools like trophies and start treating them like leverage.
