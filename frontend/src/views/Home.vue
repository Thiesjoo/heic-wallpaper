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
    toast.error("Invalid file type.");
    return;
  }

  const result = await fetch("/api/upload", {
    method: "POST",
    body: JSON.stringify({
      name: file.name,
      type: file.type,
    }),
    headers: {
      'Content-Type': 'application/json'
    }
  }).then((res) => res.json());

  if (result.error) {
    console.error(result)
    toast.error("Error uploading file.")
    return;
  }


  const {url, fields} = result.data;
  const formData = new FormData();
  Object.entries(fields as { [key: string]: string }).forEach(([key, value]) => {
    formData.append(key, value);
  });
  formData.append("file", file);

  const progressToast = toast.info("Uploading file: 0%", {
    timeout: 0,
    closeOnClick: false,
  });

  const fileUploadResult = await axios.post(url, formData, {
    onUploadProgress: function (progressEvent) {
      toast.update(progressToast, {content: `Uploading file: ${Math.round((progressEvent.loaded / progressEvent.total) * 100)}%`});
    }
  })
  toast.dismiss(progressToast)
  if (fileUploadResult.status !== 204) {
    toast.error("Error uploading file.");
    return;
  }
  toast.success("File uploaded successfully.",
      {
        onClick: () => {
          //   browse to that wallpaper
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
