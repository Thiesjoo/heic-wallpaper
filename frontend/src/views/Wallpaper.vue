<script setup lang="ts">
import { useRoute } from 'vue-router'
import Preview from '@/components/Preview.vue'
import {
    getApiWallpaperURL,
    useWallpaperStore,
    type WallpaperWithDetails,
} from '@/stores/wallpaper'
import { useUserStore } from '@/stores/user'
import { computed } from 'vue'

const SECONDS_IN_A_DAY = 60 * 60 * 24

const route = useRoute()
const id = route.params.id as string

const wallpaperStore = useWallpaperStore()
const wallpaper = await wallpaperStore.getWallpaperById(id)
const wallpaperData = computed(() => {
    return wallpaper.data || [{ i: 0, t: 0 }]
})

const baseURL = wallpaper.preview_url
const userStore = useUserStore()

function select() {
    userStore.updateWallpaper(getApiWallpaperURL(wallpaper))
}

function copyURL() {
    navigator.clipboard.writeText(getApiWallpaperURL(wallpaper))
}
</script>

<template>
    <h3 class="text-center text-l text-emerald-300 font-bolder">
        Preview all times of the live wallpaper
    </h3>

    <h3 class="text-center text-xl text-emerald-600 font-bolder">
        {{ wallpaper.name }}
    </h3>
    <h2 class="text-center text-m text-emerald-600 font-bolder">
        Created by: {{ wallpaper.created_by }}
    </h2>

    <div class="flex justify-center" v-if="userStore.loggedIn">
        <button
            class="border p-2 m-4 hover:bg-green-600 rounded-md"
            @click="select()"
        >
            Select this wallpaper
        </button>
    </div>

    <div class="flex justify-center">
        <!-- Copy URL -->
        <button
            class="w-full bg-blue-500 hover:bg-blue-700 text-white font-bold px-4 m-4 rounded"
            @click="copyURL"
        >
            Copy
        </button>
    </div>
    <main class="w-full h-full flex flex-wrap justify-center">
        <Preview
            :size="25"
            :url="baseURL.replace('preview', `${i}`)"
            v-for="{ i, t } in wallpaperData"
        >
            <span class="w-full text-center">
                Wallpaper after
                {{
                    new Date(SECONDS_IN_A_DAY * t * 1000)
                        .toISOString()
                        .slice(11, 16)
                }}</span
            >
        </Preview>
    </main>
</template>
