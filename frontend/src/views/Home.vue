<script lang="ts" setup>
import WallpaperPreviewCard from "@/components/WallpaperPreviewCard.vue";
import { fetchWallpapersFromApi } from "@/stores/wallpaper";
import Drop from "@/components/Drop.vue";
import { onDrop } from "@/utils/onDrop";
import { VuePaginatedAntComposable } from "@/utils/VuePaginatedAnt";
import Wallpaper from "@/views/Wallpaper.vue";
import { useIntervalFn, useDocumentVisibility, useIdle } from "@vueuse/core";

async function dataFunction(
  search: string,
  sort: string,
  page: number,
  pageSize: number,
) {
  const params = new URLSearchParams();
  params.append("search", search);
  params.append("sort", sort);
  params.append("page", page.toString());
  params.append("limit", pageSize.toString());

  const response = await fetchWallpapersFromApi(params);

  return {
    data: response.results,
    pagination: {
      total: response.total,
      pageSize: response.limit,
      current: response.page,
    },
  };
}

const {
  loading,
  pagination,
  data,
  search,
  pageSize,
  page,
  debouncedRefreshListView,
} = VuePaginatedAntComposable<Wallpaper>(dataFunction);

const visibility = useDocumentVisibility();
const idle = useIdle(1000 * 60);
useIntervalFn(() => {
  if (visibility.value === "visible" && !idle.value) {
    debouncedRefreshListView();
  }
}, 1000 * 10);
</script>

<template>
  <Drop text="Drop your pictures here" @drop="onDrop"></Drop>
  <h3 class="text-center text-xl w-full">
    Get your dynamic wallpapers from here:
    <a
      class="underline text-emerald-600"
      href="https://dynamicwallpaper.club/gallery"
      rel="noreferrer"
      target="_blank"
      >dynamicwallpaper.club</a
    >
  </h3>
  <a-divider></a-divider>
  <a-flex justify="center">
    <a-input-search
      v-model:value="search"
      placeholder="Looking for something?"
      style="width: 50%"
    />
  </a-flex>
  <a-divider></a-divider>
  <a-list
    :data-source="data"
    :grid="{ gutter: 16, xs: 1, sm: 1, md: 2, lg: 2, xl: 3, xxl: 4 }"
    :loading="loading"
  >
    <template #renderItem="{ item }">
      <a-list-item>
        <WallpaperPreviewCard :wallpaper="item"></WallpaperPreviewCard>
      </a-list-item>
    </template>
  </a-list>
  <a-flex justify="center">
    <a-pagination
      v-model:current="page"
      v-model:pageSize="pageSize"
      :loading="loading"
      :show-total="
        (total, range) => `${range[0]}-${range[1]} of ${total} items`
      "
      :total="pagination.total"
      hide-on-single-page
    ></a-pagination>
  </a-flex>
</template>
