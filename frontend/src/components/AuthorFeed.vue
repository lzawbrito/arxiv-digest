<script setup lang="ts">
import { ref, computed } from "vue";
import type { AuthorFeedData } from "@/types/authors";
import AuthorPaperCard from "./AuthorPaperCard.vue";

const props = defineProps<{
    feed: AuthorFeedData;
}>();

// Empty string means "all subscribed authors"
const selectedAuthor = ref<string>("");

const paperCounts = computed(() => {
    const counts: Record<string, number> = {};
    for (const author of props.feed.metadata.authors) counts[author] = 0;
    for (const paper of props.feed.papers) {
        for (const author of paper.matched_authors) {
            counts[author] = (counts[author] ?? 0) + 1;
        }
    }
    return counts;
});

const filteredPapers = computed(() => {
    if (!selectedAuthor.value) return props.feed.papers;
    return props.feed.papers.filter((paper) =>
        paper.matched_authors.includes(selectedAuthor.value),
    );
});
</script>

<template>
    <div v-if="feed.metadata.authors.length === 0" class="papers-container">
        <div class="no-papers">
            <div class="no-papers-icon">👤</div>
            <h2>No subscribed authors</h2>
            <p>Add authors under <code>subscriptions.authors</code> in config.yaml</p>
        </div>
    </div>
    <template v-else>
        <div class="controls">
            <div class="stage-selector">
                <button
                    class="stage-btn"
                    :class="{ active: selectedAuthor === '' }"
                    @click="selectedAuthor = ''"
                >
                    All Authors ({{ feed.papers.length }})
                </button>
                <button
                    v-for="author in feed.metadata.authors"
                    :key="author"
                    class="stage-btn"
                    :class="{ active: selectedAuthor === author }"
                    @click="selectedAuthor = author"
                >
                    {{ author }} ({{ paperCounts[author] }})
                </button>
            </div>

            <div class="stats">
                <div class="stat">
                    <span>Last</span>
                    <span class="stat-value">{{ feed.metadata.lookback_days }} days</span>
                </div>
            </div>
        </div>

        <div class="papers-container">
            <div v-if="filteredPapers.length === 0" class="no-papers">
                <div class="no-papers-icon">📭</div>
                <h2>No recent papers</h2>
                <p>Nothing new in the last {{ feed.metadata.lookback_days }} days</p>
            </div>
            <AuthorPaperCard v-for="paper in filteredPapers" :key="paper.arxiv_id" :paper="paper" />
        </div>
    </template>
</template>
