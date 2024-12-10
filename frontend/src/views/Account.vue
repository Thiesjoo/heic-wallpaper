<script setup lang="ts">
import { useUserStore } from "@/stores/user";
import Wallpaper from "@/components/SingleWallpaper.vue";
import {
  useWallpaperStore,
  type WallpaperWithDetails,
} from "@/stores/wallpaper";
import { computedAsync } from "@vueuse/core";
import { useRouter } from "vue-router";

const userStore = useUserStore();
const wallpaperStore = useWallpaperStore();

const router = useRouter();

if (!userStore.loggedIn) {
  console.warn("User is not logged in, redirecting to login page");
  router.push({ name: "Login" });
}

const currentWallpaper = computedAsync(async () => {
  let currentURL = userStore.user?.settings.backgroundURL;
  if (!currentURL) {
    return undefined;
  }

  currentURL = currentURL.substring(currentURL.lastIndexOf("/") + 1).trim();
  if (currentURL.length === 36) {
    return await wallpaperStore.getWallpaperById(currentURL);
  }
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
      <Wallpaper
        :wallpaper="currentWallpaper"
        v-if="currentWallpaper"
      ></Wallpaper>
    </div>
    <div v-else>You do not have a wallpaper configured with this site.</div>

    <button
      @click="userStore.reset"
      type="button"
      class="mt-5 inline-flex justify-center rounded-md border border-transparent shadow-sm px-5 py-2 bg-red-600 text-base font-medium text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 sm:w-auto sm:text-sm"
    >
      <div class="flex flex-row justify-center items-center">
        <span>Logout</span>
      </div>
    </button>
  </div>
</template>
