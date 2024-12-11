<script lang="ts" setup>
import { type Wallpaper, WallpaperStatus } from "@/stores/wallpaper";
import { computed, ref } from "vue";
import { useRouter } from "vue-router";
import formatDate from "@/utils/formatDates";

const props = defineProps<{
  wallpaper: Wallpaper;
}>();

const wallpaper = props.wallpaper;

const isLoading = computed(() => {
  return wallpaper.status === WallpaperStatus.PROCESSING;
});

const isError = computed(() => {
  return (
    wallpaper.status === WallpaperStatus.DELETED ||
    wallpaper.status === WallpaperStatus.ERROR
  );
});
const router = useRouter();

function click() {
  if (isError.value || isLoading.value) {
    return;
  }
  router.push(`/wallpaper/${wallpaper.id}`);
}

const previewError = ref(false);
const canInteract = computed(() => {
  return !isLoading.value && !isError.value && !previewError.value;
});
</script>

<template>
  <a-card
    :hoverable="canInteract"
    :loading="isLoading || previewError"
    :style="{
      cursor: canInteract ? 'pointer' : 'not-allowed',
      width: '350px',
    }"
    :title="wallpaper.name"
    @click="click"
  >
    <template #cover>
      <span v-if="isError" class="w-full text-center font-bold">
        This wallpaper is broken
      </span>
      <img
        v-else-if="!isLoading && !previewError"
        :src="wallpaper.preview_url"
        :style="{
          height: '200px',
          objectFit: 'cover',
        }"
        @error="previewError = true"
      />
    </template>
    <a-card-meta
      :description="`Created by ${wallpaper.owner.first_name}, on ${formatDate(
        wallpaper.date_created,
      )}`"
    >
    </a-card-meta>
  </a-card>
</template>

<style scoped></style>
