import { defineCollection } from 'astro:content';
import { z } from 'astro/zod';
import { file } from 'astro/loaders';
import { parse } from 'yaml';

// Publications live in cv/publications.yaml — the single source shared by the
// website and the CV. Entries are a plain YAML list (newest first); this parser
// gives each one a stable id and remembers its position so the page keeps the
// file's order.
const publications = defineCollection({
  loader: file('cv/publications.yaml', {
    parser: (text) =>
      (parse(text) as Record<string, unknown>[]).map((entry, order) => ({
        id: String(order).padStart(3, '0'),
        order,
        ...entry,
      })),
  }),
  schema: z
    .object({
      id: z.string(),
      order: z.number(),
      type: z.enum(['article', 'chapter']),
      authors: z.string(),
      year: z.number().int(),
      title: z.string(),
      note: z.string().optional(),
      journal: z.string().optional(),
      volume: z.coerce.string().optional(),
      issue: z.coerce.string().optional(),
      pages: z.coerce.string().optional(),
      source: z.string().optional(),
      doi: z.string().optional(),
      pdf: z.string().optional(),
    })
    .strict()
    .refine((p) => p.journal || p.source, {
      message: 'Each publication needs either `journal` or `source`',
    }),
});

export const collections = { publications };
