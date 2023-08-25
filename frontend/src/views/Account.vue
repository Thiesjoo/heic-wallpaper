<script setup lang="ts">
import { useUserStore } from '@/stores/user'
import Wallpaper from '@/components/SingleWallpaper.vue'
import { useWallpaperStore } from '@/stores/wallpaper'

const userStore = useUserStore()
const wallpaperStore = useWallpaperStore()
const settings = await userStore.getSettings()
let currentURL = settings.backgroundURL
currentURL = currentURL.substring(currentURL.lastIndexOf('/') + 1).trim()

const currentWallpaper =
    currentURL.length == 36
        ? await wallpaperStore.getWallpaperById(currentURL)
        : undefined
</script>
<template>
    <div v-if="userStore.loggedIn" class="flex flex-col items-center">
        <h1>Hi! You are:</h1>
        <span
            >{{ userStore?.user?.name }} with email:
            {{ userStore?.user?.email }}</span
        >
        <br />
        Actual wallpaper: <br />
        <Wallpaper
            :wallpaper="currentWallpaper"
            v-if="currentWallpaper"
        ></Wallpaper>
    </div>
</template>
