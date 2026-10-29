import { z } from "zod";

// Paper by a subscribed author (no LLM stages: every match is shown)
const AuthorPaperSchema = z.object({
    arxiv_id: z.string(),
    title: z.string(),
    authors: z.array(z.string()),
    categories: z.array(z.string()),
    abstract: z.string(),
    pdf_url: z.string(),
    abs_url: z.string(),
    published: z.string(),
    updated: z.string(),
    // Subscription names (config spelling), used for the per-author filter
    matched_authors: z.array(z.string()),
    // The same authors as spelled in this paper's author list, used for bolding
    highlight_authors: z.array(z.string()),
});

const AuthorFeedMetadataSchema = z.object({
    timestamp: z.string(),
    authors: z.array(z.string()),
    lookback_days: z.number(),
});

// Full authors.json schema
export const AuthorFeedSchema = z.object({
    metadata: AuthorFeedMetadataSchema,
    papers: z.array(AuthorPaperSchema),
});

// TypeScript types inferred from schemas
export type AuthorPaper = z.infer<typeof AuthorPaperSchema>;
export type AuthorFeedMetadata = z.infer<typeof AuthorFeedMetadataSchema>;
export type AuthorFeedData = z.infer<typeof AuthorFeedSchema>;
