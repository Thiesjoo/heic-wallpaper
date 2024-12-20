<script lang="ts" setup>
import { type Wallpaper, WallpaperStatus } from "@/stores/wallpaper";
import { computed, ref, toRefs } from "vue";
import { useRouter } from "vue-router";
import formatDate from "@/utils/formatDates";
import {
  HeartOutlined,
  PlusOutlined,
  HeartFilled,
} from "@ant-design/icons-vue";

const props = defineProps<{
  wallpaper: Wallpaper;
}>();

const { wallpaper } = toRefs(props);

const isLoading = computed(() => {
  return wallpaper.value.status === WallpaperStatus.PROCESSING;
});

const isError = computed(() => {
  return wallpaper.value.status === WallpaperStatus.ERROR;
});
const router = useRouter();

function click() {
  if (isError.value || isLoading.value) {
    return;
  }
  router.push(`/wallpaper/${wallpaper.value.id}`);
}

const previewError = ref(false);
const canInteract = computed(() => {
  return !isLoading.value && !isError.value && !previewError.value;
});

const showActions = ref(false);
</script>

<template>
  <a-card
    :hoverable="canInteract"
    @mouseenter="showActions = true"
    @mouseleave="showActions = false"
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

    <template #actions>
      <!--      TODO: Likes-->
      <!--      <heart-outlined key="setting" />-->
      <!--      <heart-filled key="setting" />-->
      <!--      TODO: Playlists/screens-->
      <!--      <plus-outlined key="edit" />-->
    </template>
  </a-card>
</template>

<style scoped></style>
