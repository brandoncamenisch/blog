export interface WorkEntry {
  title: string;
  org?: string;
  role?: string;
  description?: string;
  stack?: string[];
  learning?: string[];
  tags?: string[];
  isMilestone?: boolean;
}

export interface LifeEntry {
  title: string;
  description?: string;
  tags?: string[];
}

export interface TimelineYear {
  year: string;
  work?: WorkEntry;
  life?: LifeEntry;
}

export const timeline: TimelineYear[] = [
  {
    year: 'Jun 19, 1985',
    life: { title: 'Born', description: 'Arrived. The rest followed.' },
  },
  {
    year: '1986',
    life: { title: 'First year', description: 'Loud. Demanding. No documentation.' },
  },
  {
    year: '1987',
    life: { title: 'Language acquisition', description: 'Slow at first, then all at once.' },
  },
  {
    year: '1988',
    life: { title: 'Mobile', description: 'Began exploring systems without permission.' },
  },
  {
    year: '1989',
    life: { title: 'Asking why', description: 'Started asking why. Rarely satisfied with the answer.' },
  },
  {
    year: '1990',
    life: { title: 'Enrolled in school', description: 'First structured environment. Mixed reviews.', tags: ['education'] },
  },
  {
    year: '1991',
    life: { title: 'First video game', description: 'Something clicked that has not unclicked since.', tags: ['games'] },
  },
  {
    year: '1992',
    life: { title: 'Reading', description: 'Learned to read well. Books before screens.' },
  },
  {
    year: '1993',
    life: { title: 'Building things', description: 'First things built with hands. Lego, mostly. Always with instructions once, then without.' },
  },
  {
    year: '1994',
    life: { title: 'Changed schools', description: 'New environment. Adapted faster than expected.' },
  },
  {
    year: '1995',
    life: { title: 'High school', description: 'Broader social graph, harder problems. First real exposure to computers.', tags: ['education'] },
  },
  {
    year: '1996',
    life: { title: 'First computer access', description: 'The internet was slow and full of things. Spent more time online than offline.', tags: ['internet'] },
  },
  {
    year: '1997',
    life: { title: 'Taking it apart', description: 'Started disassembling machines to see how they worked. Put most of them back together.', tags: ['hardware'] },
  },
  {
    year: '1998',
    life: { title: 'Late nights online', description: 'IRC, forums, early web. Something about the asynchronous nature of it felt right.', tags: ['internet', 'community'] },
  },
  {
    year: '1999',
    life: { title: 'Last year before everything broke', description: 'Graduated. Everyone said the world was ending at midnight. It did not.' },
  },
  {
    year: '2000',
    work: {
      title: 'First IT role',
      org: 'Small ISP',
      role: 'Helpdesk / Desktop Support',
      description: 'Entry point into the industry. Supported end users, swapped hardware, learned to read error messages before Googling them.',
      stack: ['Windows 98', 'Windows NT', 'dial-up networking'],
      learning: ['TCP/IP fundamentals', 'hardware repair', 'cable termination'],
      tags: ['helpdesk', 'hardware', 'networking'],
    },
    life: { title: 'Moved out', description: 'Two jobs, one apartment, no savings. Worked anyway.' },
  },
  {
    year: '2001',
    work: {
      title: 'Linux administration begins',
      org: 'Small ISP',
      role: 'Junior Systems Administrator',
      description: 'Moved from Windows support to managing Red Hat servers. Bash replaced clicking. Never went back.',
      stack: ['Red Hat Linux', 'Apache', 'sendmail', 'bash'],
      learning: ['shell scripting', 'cron', 'user management', 'log analysis'],
      tags: ['linux', 'sysadmin', 'bash'],
    },
    life: { title: 'Learning everything at once', description: 'Work, study, adapt. Not enough sleep. Did it anyway.' },
  },
  {
    year: '2002',
    work: {
      title: 'First web stack in production',
      org: 'Regional web agency',
      role: 'Systems Administrator',
      description: 'Stood up LAMP stacks, managed DNS, deployed client sites. First time owning something end-to-end in production.',
      stack: ['Linux', 'Apache', 'MySQL', 'PHP', 'BIND DNS'],
      learning: ['LAMP stack', 'DNS management', 'FTP deployment', 'basic SQL'],
      tags: ['lamp', 'web', 'dns', 'mysql'],
    },
    life: { title: 'Found a rhythm', description: 'Modest but real. First year that felt sustainable.' },
  },
  {
    year: '2003',
    work: {
      title: 'Promoted to Systems Administrator',
      org: 'Regional web agency',
      role: 'Systems Administrator',
      description: 'Took ownership of all server infrastructure. Wrote the backup strategy, managed on-call, handled uptime SLAs.',
      stack: ['Linux', 'Apache', 'Nagios', 'rsync', 'cron'],
      learning: ['monitoring', 'backup strategy', 'incident response', 'SLAs'],
      tags: ['sysadmin', 'infrastructure', 'monitoring'],
      isMilestone: true,
    },
    life: { title: 'First lease signed alone', description: 'Stability. Small but mine.' },
  },
  {
    year: '2004',
    work: {
      title: 'Datacenter operations',
      org: 'Managed hosting provider',
      role: 'Systems Engineer',
      description: 'Managed physical rack infrastructure at scale. Racked, cabled, configured. Understood hardware failure modes firsthand.',
      stack: ['CentOS', 'Cisco IOS', 'IPMI', 'iSCSI', 'NFS'],
      learning: ['networking hardware', 'SAN storage', 'VLAN configuration', 'physical security'],
      tags: ['datacenter', 'hardware', 'networking', 'cisco'],
    },
    life: { title: 'Long hours', description: 'Learning what I could actually handle. More than I thought.' },
  },
  {
    year: '2005',
    work: {
      title: 'Automation and scripting',
      org: 'Managed hosting provider',
      role: 'Senior Systems Engineer',
      description: 'Stopped doing things manually that could be scripted. Perl for glue, Python for everything else. Fewer 2am pages.',
      stack: ['Python', 'Perl', 'bash', 'cron', 'expect'],
      learning: ['Python', 'Perl', 'automation patterns', 'config management concepts'],
      tags: ['python', 'perl', 'automation', 'scripting'],
    },
    life: { title: 'First real hardware purchase', description: 'Bought first machine with my own money. Still have the receipt.', tags: ['hardware'] },
  },
  {
    year: '2006',
    work: {
      title: 'Senior Systems Engineer',
      org: 'Managed hosting provider',
      role: 'Senior Systems Engineer',
      description: 'First role with architecture ownership. Designed infrastructure for new hosting tiers, mentored junior admins.',
      stack: ['Python', 'Linux', 'Xen', 'Puppet (early)', 'MySQL replication'],
      learning: ['infrastructure architecture', 'virtualization', 'mentorship', 'capacity planning'],
      tags: ['architecture', 'virtualization', 'xen', 'puppet'],
      isMilestone: true,
    },
    life: { title: 'New city', description: 'First major move. Left the familiar. Took a few months to stop feeling like a visitor.' },
  },
  {
    year: '2007',
    work: {
      title: 'Crossed into software engineering',
      org: 'SaaS company',
      role: 'Infrastructure Engineer',
      description: 'Internal tooling grew into real applications. Started writing Python services, not just scripts. The line between ops and dev blurred.',
      stack: ['Python', 'Django', 'PostgreSQL', 'nginx', 'Fabric'],
      learning: ['Django', 'PostgreSQL', 'REST APIs', 'deployment automation'],
      tags: ['python', 'django', 'postgresql', 'fullstack'],
    },
    life: { title: 'Settled in', description: 'Made tools that fit my hand. Started feeling at home in the work and the city.', tags: ['vim', 'tools'] },
  },
  {
    year: '2008',
    work: {
      title: 'Joined a startup',
      org: 'Early-stage startup',
      role: 'Engineer',
      description: 'Small team, undefined roles. Wrote backend services, managed infra, ran deploys. Wore every hat.',
      stack: ['Ruby on Rails', 'Python', 'MySQL', 'nginx', 'EC2 (early AWS)'],
      learning: ['Ruby on Rails', 'AWS EC2', 'product development', 'startup operations'],
      tags: ['startup', 'rails', 'aws', 'fullstack'],
    },
    life: { title: 'Economic chaos in the background', description: 'Kept head down and shipped. Some things you just have to work through.' },
  },
  {
    year: '2009',
    work: {
      title: 'Navigated a downturn',
      org: 'Early-stage startup',
      role: 'Lead Engineer',
      description: 'Company contracted hard. Led a technical pivot with a reduced team. Scope narrowed, focus sharpened. Product survived.',
      stack: ['Python', 'Flask', 'MySQL', 'AWS', 'Varnish'],
      learning: ['technical leadership', 'scope reduction', 'performance optimization', 'caching'],
      tags: ['leadership', 'flask', 'performance', 'caching'],
      isMilestone: true,
    },
    life: { title: 'Hard year', description: 'Emerged on the other side more certain about what mattered. The list got shorter.' },
  },
  {
    year: '2010',
    work: {
      title: 'Open source and community',
      org: 'Consulting (independent)',
      role: 'Software Engineer / Consultant',
      description: 'Went independent part-time. First open source patches merged. Started engaging with the Python and ops communities.',
      stack: ['Python', 'Django', 'Chef', 'AWS', 'git'],
      learning: ['open source contribution', 'Chef', 'infrastructure as code', 'git workflows'],
      tags: ['open-source', 'chef', 'iac', 'community'],
    },
    life: { title: 'Found peers', description: 'First people in the work who felt like real peers. That changed everything about how the work felt.', tags: ['community'] },
  },
  {
    year: '2011',
    work: {
      title: 'Technical Lead',
      org: 'Mid-size product company',
      role: 'Technical Lead',
      description: 'Led a product engineering team. Owned architecture decisions, ran code review, mentored juniors. Shipped production features weekly.',
      stack: ['Python', 'Django', 'PostgreSQL', 'Celery', 'Redis', 'AWS'],
      learning: ['technical leadership', 'Celery', 'Redis', 'distributed task queues', 'mentorship'],
      tags: ['leadership', 'django', 'redis', 'celery', 'mentorship'],
      isMilestone: true,
    },
    life: { title: 'Longer view', description: 'Started thinking in years instead of sprints. The urgency became more selective.' },
  },
  {
    year: '2012',
    work: {
      title: 'Distributed systems',
      org: 'Mid-size product company',
      role: 'Senior Software Engineer',
      description: 'Designed systems that scaled horizontally. CAP theorem stopped being theory. Learned where consistency and availability actually trade off.',
      stack: ['Python', 'Cassandra', 'Kafka', 'AWS', 'HAProxy'],
      learning: ['Cassandra', 'Kafka', 'event streaming', 'distributed consistency', 'HAProxy'],
      tags: ['distributed-systems', 'kafka', 'cassandra', 'scalability'],
    },
    life: { title: 'Physical health', description: 'Started taking it seriously. Couldn\'t keep ignoring the cost of the schedule.', tags: ['health'] },
  },
  {
    year: '2013',
    work: {
      title: 'Engineering Manager',
      org: 'Growth-stage startup',
      role: 'Engineering Manager',
      description: 'First management role. Hired, onboarded, ran 1:1s, wrote performance reviews. Discovered people problems are harder than technical ones.',
      stack: ['Node.js', 'PostgreSQL', 'AWS', 'Terraform (early)', 'GitHub'],
      learning: ['engineering management', 'hiring', 'performance feedback', 'Node.js', 'Terraform'],
      tags: ['management', 'hiring', 'node', 'terraform'],
    },
    life: { title: 'Got a dog', description: 'Priorities permanently and irreversibly reordered.', tags: ['dog'] },
  },
  {
    year: '2014',
    work: {
      title: 'Grew and shipped a platform',
      org: 'Growth-stage startup',
      role: 'Director of Engineering',
      description: 'Scaled the team from 3 to 8. Delivered a multi-tenant platform handling meaningful production load.',
      stack: ['Go', 'PostgreSQL', 'gRPC', 'Kubernetes (early)', 'AWS', 'Terraform'],
      learning: ['Go', 'gRPC', 'Kubernetes', 'multi-tenancy patterns', 'team scaling'],
      tags: ['go', 'grpc', 'kubernetes', 'platform', 'team-building'],
      isMilestone: true,
    },
    life: { title: 'Hardest year', description: 'Professionally and personally. Navigated both. Some things didn\'t survive. The important ones did.' },
  },
  {
    year: '2015',
    work: {
      title: 'Went independent',
      org: 'Self-employed',
      role: 'Independent Engineer / Consultant',
      description: 'Left the org to consult. Traded stability for direct ownership of the work.',
      stack: ['Go', 'Python', 'Kubernetes', 'Terraform', 'AWS', 'GCP'],
      learning: ['GCP', 'consulting practice', 'contract negotiation', 'client management'],
      tags: ['consulting', 'independent', 'go', 'gcp', 'terraform'],
      isMilestone: true,
    },
    life: { title: 'Deliberate simplification', description: 'Kept only what worked. Cleared the rest.', tags: ['minimalism'] },
  },
  {
    year: '2016',
    work: {
      title: 'Consulting practice',
      org: 'Multiple clients',
      role: 'Principal Consultant',
      description: 'Infrastructure, backend systems, team coaching. Different problem domains every quarter.',
      stack: ['Go', 'Python', 'Kubernetes', 'Terraform', 'Postgres', 'gRPC', 'AWS'],
      learning: ['cross-domain architecture', 'technical coaching', 'systems design review'],
      tags: ['consulting', 'architecture', 'coaching', 'kubernetes'],
    },
    life: { title: 'Traveled more', description: 'Different places, different timezones, same laptop. Perspective shifted.', tags: ['travel'] },
  },
  {
    year: '2017',
    work: {
      title: 'Burnout and reset',
      org: 'Self-employed',
      role: '—',
      description: 'Overextended across too many clients. Stepped back, reduced scope, and rebuilt sustainable working patterns.',
      stack: [],
      learning: ['pacing', 'scope management', 'sustainable work', 'boundaries'],
      tags: ['health', 'boundaries', 'recovery'],
    },
    life: { title: 'Stillness', description: 'Necessary. Did not feel like progress at the time. Was.', tags: ['health', 'recovery'] },
  },
  {
    year: '2018',
    work: {
      title: 'Staff Engineer',
      org: 'Series B company',
      role: 'Staff Software Engineer',
      description: 'Returned to an org on the IC track. High autonomy, cross-team technical influence.',
      stack: ['Go', 'Rust (learning)', 'Kafka', 'Kubernetes', 'Postgres', 'Temporal'],
      learning: ['Rust', 'Temporal', 'staff eng patterns', 'technical strategy'],
      tags: ['staff-eng', 'go', 'rust', 'kafka', 'temporal'],
    },
    life: { title: 'Rebuilt', description: 'Slower. Sturdier. Better defaults.' },
  },
  {
    year: '2019',
    work: {
      title: 'Full containerization',
      org: 'Series B company',
      role: 'Staff Software Engineer',
      description: 'Led migration of legacy services to Docker and Kubernetes. Dev/prod parity finally real.',
      stack: ['Kubernetes', 'Docker', 'Helm', 'ArgoCD', 'Terraform', 'Go'],
      learning: ['ArgoCD', 'Helm', 'GitOps', 'platform engineering', 'operator pattern'],
      tags: ['docker', 'kubernetes', 'gitops', 'argocd', 'helm'],
    },
    life: { title: 'Bought a place', description: 'First time owning something fixed to the earth. Strange and good.', tags: ['home'] },
  },
  {
    year: '2020',
    work: {
      title: 'Remote-first infrastructure',
      org: 'Series B company',
      role: 'Staff Software Engineer',
      description: 'Helped the org adapt infrastructure and async process for fully distributed engineering.',
      stack: ['Go', 'Kubernetes', 'Postgres', 'Pulumi', 'Slack API'],
      learning: ['Pulumi', 'async engineering practices', 'remote team tooling'],
      tags: ['remote', 'pulumi', 'async', 'devex'],
    },
    life: { title: 'Everything remote', description: 'Surprisingly fine, then not, then fine again. The baseline shifted.' },
  },
  {
    year: '2021',
    work: {
      title: 'Principal Engineer',
      org: 'Series B company',
      role: 'Principal Software Engineer',
      description: 'Promoted to principal. Scope expanded to org-wide technical direction, cross-team alignment, and engineering hiring bar.',
      stack: ['Go', 'Rust', 'Kubernetes', 'Kafka', 'Postgres', 'Temporal'],
      learning: ['org-level technical strategy', 'hiring bar calibration', 'RFC process'],
      tags: ['principal', 'leadership', 'strategy', 'architecture'],
      isMilestone: true,
    },
    life: { title: 'Started writing again', description: 'Notes that became posts. Posts that became signals. The rest are hallucinations.', tags: ['writing'] },
  },
  {
    year: '2022',
    work: {
      title: 'Developer experience focus',
      org: 'Series B company',
      role: 'Principal Software Engineer',
      description: 'Shifted primary focus to internal developer experience. CI pipelines, local dev tooling, observability, service onboarding.',
      stack: ['Go', 'Dagger', 'GitHub Actions', 'OpenTelemetry', 'Grafana', 'Prometheus'],
      learning: ['Dagger', 'OpenTelemetry', 'observability design', 'DX metrics'],
      tags: ['dx', 'platform-eng', 'otel', 'grafana', 'ci-cd'],
    },
    life: { title: 'Health as practice', description: 'Not a crisis response. A routine. Took long enough.', tags: ['health'] },
  },
  {
    year: '2023',
    work: {
      title: 'Independent again',
      org: 'Self-employed',
      role: 'Independent Engineer',
      description: 'Left the org. Returned to independent work with more clarity about what actually matters.',
      stack: ['Go', 'TypeScript', 'Astro', 'Docker', 'Terraform'],
      learning: ['Astro', 'TypeScript', 'static site architecture', 'edge deployment'],
      tags: ['independent', 'astro', 'typescript', 'go'],
      isMilestone: true,
    },
    life: { title: 'More deliberate', description: 'Said no more. Built more. The ratio improved.' },
  },
  {
    year: '2024',
    work: {
      title: 'Building in public',
      org: 'Self-employed',
      role: 'Independent Engineer',
      description: 'Launched this site. Writing alongside building. Generative tooling integrated into the workflow.',
      stack: ['Astro', 'TypeScript', 'Docker', 'ComfyUI', 'Ollama', 'Python'],
      learning: ['ComfyUI', 'Ollama', 'LLM-assisted workflows', 'generative image pipelines'],
      tags: ['writing', 'astro', 'comfyui', 'ollama', 'ai-tooling'],
    },
    life: { title: 'The writing connected things', description: '3,504 posts and still figuring out what it is. That is fine.', tags: ['writing', 'blog'] },
  },
  {
    year: '2025',
    work: {
      title: 'Deepening the practice',
      org: 'Self-employed',
      role: 'Independent Engineer',
      description: 'Less context-switching, more sustained work on hard problems. Focused on craft over throughput.',
      stack: ['Go', 'Rust', 'TypeScript', 'Kubernetes', 'Terraform'],
      learning: ['Rust (deepening)', 'eBPF', 'WASM', 'systems programming'],
      tags: ['rust', 'ebpf', 'wasm', 'systems', 'craft'],
    },
    life: { title: 'Fewer things, done more thoroughly', description: 'The discipline of finishing. Harder than starting.' },
  },
  {
    year: '2026',
    work: {
      title: 'Still compiling',
      org: 'Self-employed',
      role: 'Independent Engineer',
      description: 'Present tense.',
      stack: [],
      learning: [],
      tags: [],
    },
    life: { title: 'Still here', description: 'Somewhere between signal and hallucination.' },
  },
];
