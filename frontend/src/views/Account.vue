<script setup lang="ts">
import { useUserStore } from "@/stores/user";
import { useWallpaperStore } from "@/stores/wallpaper";
import { computedAsync } from "@vueuse/core";
import { useRouter } from "vue-router";
import WallpaperPreviewCard from "@/components/WallpaperPreviewCard.vue";

const userStore = useUserStore();
const wallpaperStore = useWallpaperStore();

const router = useRouter();

if (!userStore.loggedIn) {
  router.push("/login");
}

const currentWallpaper = computedAsync(async () => {
  let currentURL = userStore.user?.settings.backgroundURL;
  if (!currentURL) {
    return undefined;
  }

  const host = new URL(currentURL).hostname;
  if (host !== window.location.hostname) {
    return undefined;
  }

  if (currentURL[currentURL.length - 1] !== "/") {
    currentURL = currentURL + "/";
  }

  const secondLastSlash = currentURL.lastIndexOf("/", currentURL.length - 2);
  currentURL = currentURL
    .substring(secondLastSlash + 1, currentURL.length - 1)
    .trim();
  return await wallpaperStore.getWallpaperById(currentURL);
}, undefined);
</script>
<template>
  <div v-if="userStore.loggedIn" class="flex flex-col items-center space-y-3">
    <h1 class="font-bold text-lg">Hi! You are:</h1>
    <span>
      <span class="font-extrabold"> {{ userStore?.user?.name.first }} </span>
      with email:
      <span class="italic"> {{ userStore?.user?.email }}</span>
    </span>

    <div class="flex flex-col items-center" v-if="currentWallpaper">
      Actual wallpaper
      <template v-if="currentWallpaper">
        <WallpaperPreviewCard
          :wallpaper="currentWallpaper"
        ></WallpaperPreviewCard>
      </template>
    </div>
    <div v-else>You do not have a wallpaper configured with this site.</div>
  </div>
</template>
