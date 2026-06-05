import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const chapters = defineCollection({
  // Load the markdown chapters from src/content/chapters/*.md.
  // The id is the filename without extension (e.g. "01-introduction"),
  // which keeps lexical ordering and makes a clean URL slug.
  loader: glob({ pattern: '**/*.md', base: './src/content/chapters' }),
  schema: z.object({
    title: z.string(),
    // Numbered chapters are numbers (1..13); the appendix is the string "A".
    chapter: z.union([z.number(), z.string()]),
  }),
});

export const collections = { chapters };
