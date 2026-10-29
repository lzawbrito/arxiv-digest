<script setup lang="ts">
import { ref } from "vue";
import type { AuthorPaper } from "@/types/authors";
import { formatShortDate } from "@/utils/formatters";
import MarkdownRenderer from "./MarkdownRenderer.vue";

const props = defineProps<{
    paper: AuthorPaper;
}>();

const abstractExpanded = ref(false);

function isSubscribed(author: string): boolean {
    return props.paper.highlight_authors.includes(author);
}
</script>

<template>
    <div class="paper-card">
        <div class="paper-header">
            <div class="paper-title">
                <a :href="paper.abs_url" target="_blank">
                    <MarkdownRenderer :content="paper.title" :inline="true" />
                </a>
            </div>
            <div class="stage-badges">
                <span class="stage-badge date-badge" :title="`Submitted ${paper.published}`">
                    {{ formatShortDate(paper.published) }}
                </span>
            </div>
        </div>

        <div class="paper-meta">
            <div class="authors author-list">
                <strong><FontAwesomeIcon icon="users" class="meta-icon" />Authors:</strong>
                {{ " " }}
                <template v-for="(author, i) in paper.authors" :key="author">
                    <span :class="{ 'subscribed-author': isSubscribed(author) }">{{ author }}</span
                    ><template v-if="i < paper.authors.length - 1">, </template>
                </template>
            </div>
            <div v-if="paper.categories.length > 0" class="categories">
                <strong><FontAwesomeIcon icon="tags" class="meta-icon" />Categories:</strong>
                <span v-for="cat in paper.categories" :key="cat" class="category-tag">
                    {{ cat }}
                </span>
            </div>
        </div>

        <button
            class="abstract-toggle"
            :class="{ expanded: abstractExpanded }"
            @click="abstractExpanded = !abstractExpanded"
        >
            <FontAwesomeIcon
                icon="chevron-right"
                class="abstract-toggle-icon"
                :class="{ expanded: abstractExpanded }"
            />
            <span>Abstract</span>
        </button>
        <div class="paper-abstract" :class="{ expanded: abstractExpanded }">
            <MarkdownRenderer :content="paper.abstract" :inline="true" />
        </div>

        <a class="conversation-btn" :href="paper.pdf_url" target="_blank">
            <FontAwesomeIcon icon="file-pdf" />
            <span>PDF</span>
        </a>
    </div>
</template>

<style scoped>
.meta-icon {
    margin-right: 5px;
    width: 16px;
    line-height: 1em;
    text-align: center;
    color: var(--accent-color);
    vertical-align: middle;
}

/* Long author lists wrap here instead of truncating, so subscribed names stay visible */
.author-list {
    white-space: normal;
}

.subscribed-author {
    font-weight: 600;
    color: var(--accent-color);
}

/* Titles go through MarkdownRenderer (for math); keep the card's title typography */
.paper-title :deep(.markdown-renderer) {
    display: inline;
    font-size: inherit;
    line-height: inherit;
    color: inherit;
}

.date-badge {
    background: var(--border-color);
    color: var(--text-color);
}

.conversation-btn {
    text-decoration: none;
}
</style>
