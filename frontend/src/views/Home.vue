<script setup lang="ts">
import SingleWallpaper from '@/components/SingleWallpaper.vue'
import {useWallpaperStore, WallpaperStatus} from '@/stores/wallpaper'
import {computed} from 'vue'
import Drop from "@/components/Drop.vue";
import {useToast} from "vue-toastification";
import axios from "axios";

const wallpaperStore = useWallpaperStore()
const toast = useToast();

const activeWallpapers = computed(() => {
  return wallpaperStore.wallpapers.filter(
      (wallpaper) => wallpaper.status === WallpaperStatus.READY
  )
})
const pendingWallpapers = computed(() => {
  return wallpaperStore.wallpapers.filter(
      (wallpaper) => wallpaper.status !== WallpaperStatus.READY
  )
})

const allowedTypes = ["image/jpeg", "image/png", "image/gif", "image/heif", "image/heic"];

async function onDrop(file: File) {
  if (!allowedTypes.includes(file.type)) {
    if (file.name.endsWith(".heic") || file.name.endsWith(".heif")) {
      console.warn("No type for: ", file)
    } else {
      console.warn(file)
      toast.error("Invalid file type.");
      return;
    }
  }

  const presignedURLResult = await fetch("/api/upload", {
    method: "POST",
    body: JSON.stringify({
      name: file.name,
      type: file.type,
    }),
    headers: {
      'Content-Type': 'application/json'
    }
  }).then((res) => res.json());

  if (presignedURLResult.error) {
    console.error(presignedURLResult)
    toast.error("Error uploading file.")
    return;
  }

  const url = presignedURLResult.data;
  const {key, uid} = presignedURLResult;

  const progressToast = toast.info("Uploading file: 0%", {
    timeout: 0,
    closeOnClick: false,
  });

  const fileUploadResult = await axios.put(url, file, {
    headers: {
      'Content-Type': file.type,
    },
    onUploadProgress: function (progressEvent) {
      const percent = progressEvent.total ? Math.round((progressEvent.loaded / progressEvent.total) * 100) : 0;
      toast.update(progressToast, {content: `Uploading file: ${percent}%`});
    }
  })
  toast.dismiss(progressToast)
  if (fileUploadResult.status !== 200) {
    toast.error("Error uploading file.");
    return;
  }

  const completeResult = await axios.post("/api/upload/complete",
      {
        key: key,
        uid: uid,
      }
  )

  if (completeResult.status !== 202) {
    toast.error("Error processing file.");
    return;
  }

  toast.success("File uploaded successfully.",
      {
        onClick: () => {
          // TODO: browse to that wallpaper
        }
      })
}
</script>

<template>
  <Drop @drop='onDrop' text="Drop your pictures here">
  </Drop>
  <h2 class="text-center text-4xl w-full m-3">
    Drop your wallpapers anywhere on this page
  </h2>
  <h3 class="text-center text-xl w-full">
    Get your dynamic wallpapers from here:
    <a
        class="underline text-emerald-600"
        href="https://dynamicwallpaper.club/gallery"
        target="_blank"
        rel="noreferrer"
    >dynamicwallpaper.club</a
    >
  </h3>
  <section class="w-full mr-5 ml-5 flex justify-center flex-col">
    <h3 class="text-center text-xl text-emerald-300">
      All available wallpapers
    </h3>
    <div
        id="content"
        class="w-full h-full flex items-center justify-center flex-wrap"
    >
            <span
                class="text-red-600 w-full text-center"
                v-if="wallpaperStore.lastError"
            >{{ wallpaperStore.lastError }}</span
            >
      <SingleWallpaper
          :wallpaper="wallpaper"
          v-for="wallpaper in activeWallpapers"
      ></SingleWallpaper>
    </div>

    <h3
        class="text-center text-xl text-emerald-300"
        v-if="pendingWallpapers.length > 0"
    >
      All pending wallpapers
    </h3>
    <div
        id="content"
        class="w-full h-full flex items-center justify-center flex-wrap"
    >
      <SingleWallpaper
          :wallpaper="wallpaper"
          v-for="wallpaper in pendingWallpapers"
      ></SingleWallpaper>
    </div>
  </section>
</template>

<style>
.dropzone {
  text-align: center;
  margin-left: 15px;
  margin-bottom: 15px;
  margin-top: 15px;
  width: 70vw;

  display: flex;
  justify-content: center;
  align-items: center;

  --dropzone-min-height: 150px;
}
</style>
