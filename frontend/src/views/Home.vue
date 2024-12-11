<script lang="ts" setup>
import WallpaperPreviewCard from "@/components/WallpaperPreviewCard.vue";
import { useWallpaperStore, WallpaperStatus } from "@/stores/wallpaper";
import Drop from "@/components/Drop.vue";
import { onDrop } from "@/utils/onDrop";
import { computed, ref, watch } from "vue";

const wallpaperStore = useWallpaperStore();

const search = ref("");
const searchDebounced = ref("");

let debounceTimeout: number | undefined;
watch(search, () => {
  if (debounceTimeout) {
    clearTimeout(debounceTimeout);
  }
  debounceTimeout = setTimeout(() => {
    searchDebounced.value = search.value;
  }, 300);
});

const data = computed(() => {
  return wallpaperStore.wallpapers.filter((wallpaper) => {
    return wallpaper.name
      .toLowerCase()
      .includes(searchDebounced.value.toLowerCase());
  });
});
</script>

<template>
  <Drop text="Drop your pictures here" @drop="onDrop"> </Drop>
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
      @search="searchDebounced = search"
    />
  </a-flex>
  <a-divider></a-divider>
  <a-list
    :grid="{ gutter: 16, xs: 1, sm: 1, md: 2, lg: 2, xl: 3, xxl: 4 }"
    :data-source="data"
    :loading="!wallpaperStore.isFetched"
  >
    <template #renderItem="{ item }">
      <a-list-item>
        <WallpaperPreviewCard :wallpaper="item"></WallpaperPreviewCard>
      </a-list-item>
    </template>
    <!--   TODO:  Pagination or infinite scroll-->
  </a-list>
</template>
