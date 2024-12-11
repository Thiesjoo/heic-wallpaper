<script lang="ts" setup>
import { useRoute } from "vue-router";
import { getApiWallpaperURL, useWallpaperStore } from "@/stores/wallpaper";
import { useUserStore } from "@/stores/user";
import { computed } from "vue";
import formatDate from "@/utils/formatDates";
import ImagePreviewCard from "@/components/ImagePreviewCard.vue";

const SECONDS_IN_A_DAY = 60 * 60 * 24;

const route = useRoute();
const id = route.params.id as string;

const wallpaperStore = useWallpaperStore();
const wallpaper = await wallpaperStore.getWallpaperById(id);
const wallpaperData = computed(() => {
  return wallpaper.data || [{ i: 0, t: 0 }];
});

const baseURL = wallpaper.preview_url;
const userStore = useUserStore();

function select() {
  userStore.updateWallpaper(wallpaper.id);
}

function copyURL() {
  navigator.clipboard.writeText(getApiWallpaperURL(wallpaper));
}
</script>

<template>
  <h1 class="text-center text-2xl text-emerald-300 font-bolder">
    {{ wallpaper.name }}
  </h1>
  <h2 class="text-center text-m text-emerald-600 font-bolder">
    Created by: {{ wallpaper.owner.first_name }} {{ wallpaper.owner.last_name }}
  </h2>
  <h2 class="text-center text-m text-emerald-600 font-bolder">
    Created at: {{ formatDate(wallpaper.date_created) }}
    <template v-if="wallpaper.date_created !== wallpaper.date_modified">
      and last updated at: {{ formatDate(wallpaper.date_modified) }}
    </template>
  </h2>

  <div class="flex justify-center max-w-50vw">
    <div v-if="userStore.loggedIn" class="flex justify-center m-2">
      <a-button :loading="userStore.loading" @click="select()">
        Set this as your wallpaper
      </a-button>
    </div>

    <div class="flex justify-center m-2">
      <a-button @click="copyURL"> Copy URL </a-button>
    </div>
  </div>

  <a-divider></a-divider>
  <a-list
    :data-source="wallpaperData"
    :grid="{ gutter: 16, xs: 1, sm: 1, md: 2, lg: 3, xl: 4, xxl: 5 }"
    :loading="!wallpaperStore.isFetched"
  >
    <template #renderItem="{ item: { i, t } }">
      <a-list-item>
        <ImagePreviewCard :url="baseURL.replace('preview', `${i}`)">
          <span class="w-full text-center">
            Wallpaper after
            {{
              new Date(SECONDS_IN_A_DAY * t * 1000).toISOString().slice(11, 16)
            }}
          </span>
        </ImagePreviewCard>
      </a-list-item>
    </template>
  </a-list>
</template>
