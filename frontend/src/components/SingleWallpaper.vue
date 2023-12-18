<script setup lang="ts">
import {getApiWallpaperURL, type Wallpaper} from '@/stores/wallpaper'
import {WallpaperStatus} from '@/stores/wallpaper'
import Preview from './Preview.vue'
import {computed} from 'vue'
import {useUserStore} from '@/stores/user'
import router from '@/router'
import {getRouterWallpaperURL} from '@/stores/wallpaper'

const loadingURL = 'https://media.giphy.com/media/3oEjI6SIIHBdRxXI40/giphy.gif'
const errorURL =
    'https://w7.pngwing.com/pngs/595/505/png-transparent-computer-icons-error-closeup-miscellaneous-text-logo.png'

const props = defineProps<{
  wallpaper: Wallpaper
}>()

const userStore = useUserStore()
const wallpaper = props.wallpaper

const isLoading = computed(() => {
  return wallpaper.status === WallpaperStatus.PROCESSING
})

const isError = computed(() => {
  return (
      wallpaper.status === WallpaperStatus.DELETED ||
      wallpaper.status === WallpaperStatus.ERROR
  )
})

const wallpaperURL = computed(() => {
  if (isError.value) {
    return errorURL
  }
  if (isLoading.value) {
    return loadingURL
  }
  return wallpaper.preview_url
})

function copyURL() {
  navigator.clipboard.writeText(getApiWallpaperURL(wallpaper))
}

function openURL() {
  router.push(getRouterWallpaperURL(wallpaper))
}

function updateWallpaper() {
  userStore.updateWallpaper(getApiWallpaperURL(wallpaper))
}

function openURLOfError() {
  if (isError.value || isLoading.value) {
    if (wallpaper.error && wallpaper.error.startsWith('/api/tasks')) {
      window.location.href = wallpaper.error
    }
  }
}


</script>

<template>
  <div @click="openURLOfError">
    <Preview :url="wallpaperURL" :size="20">
        <span class="w-full text-center font-bold" v-if="!isError">{{
            wallpaper.name
          }}</span>
      <span class="w-full text-center font-bold" v-if="isError"
      >This wallpaper is broken</span
      >
      <!-- Show 3 buttons horizontal -->
      <div class="flex flex-row h-16" v-if="!isLoading && !isError">
        <!-- Copy URL -->
        <button
            class="w-full bg-blue-500 hover:bg-blue-700 text-white font-bold px-4 m-4 rounded"
            @click="copyURL"
        >
          Copy
        </button>
        <!-- Open button -->
        <button
            class="w-full bg-blue-500 hover:bg-blue-700 text-white font-bold px-4 m-4 rounded"
            @click="openURL"
        >
          Open
        </button>

        <!-- Select button -->
        <button
            class="w-full bg-blue-500 hover:bg-blue-700 text-white font-bold px-4 m-4 rounded"
            @click="updateWallpaper"
            v-if="userStore.loggedIn"
        >
          Set
        </button>
      </div>
    </Preview>
  </div>
</template>

<style scoped>
h1 {
  font-weight: 500;
  font-size: 2.6rem;
  position: relative;
  top: -10px;
}

h3 {
  font-size: 1.2rem;
}

.greetings h1,
.greetings h3 {
  text-align: center;
}

@media (min-width: 1024px) {
  .greetings h1,
  .greetings h3 {
    text-align: left;
  }
}
</style>
