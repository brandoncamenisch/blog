import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const work = defineCollection({
	loader: glob({ base: './src/content/work', pattern: '**/*.{md,mdx}' }),
	schema: ({ image }) =>
		z.object({
			title: z.string(),
			description: z.string(),
			pubDate: z.coerce.date(),
			updatedDate: z.coerce.date().optional(),
			heroImage: z.optional(image()),
			generatedHeroImage: z.string().optional(),
			reviewed: z.boolean().optional(),
			hallucination: z.boolean().optional(),
			signa: z.boolean().optional(),
			tags: z.array(z.string()).optional(),
			generatedImages: z
				.array(
					z.object({
						id: z.string().regex(/^[a-z0-9-]+$/),
						alt: z.string(),
						caption: z.string().optional(),
						brief: z.string(),
					}),
				)
				.optional(),
		}),
});

const life = defineCollection({
	loader: glob({ base: './src/content/life', pattern: '**/*.{md,mdx}' }),
	schema: ({ image }) =>
		z.object({
			title: z.string(),
			description: z.string(),
			pubDate: z.coerce.date(),
			updatedDate: z.coerce.date().optional(),
			heroImage: z.optional(image()),
			generatedHeroImage: z.string().optional(),
			reviewed: z.boolean().optional(),
			hallucination: z.boolean().optional(),
			signa: z.boolean().optional(),
			tags: z.array(z.string()).optional(),
		}),
});

export const collections = { work, life };
