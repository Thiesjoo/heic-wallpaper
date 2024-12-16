<script lang="ts" setup>
import WallpaperPreviewCard from "@/components/WallpaperPreviewCard.vue";
import { fetchWallpapersFromApi, type Wallpaper } from "@/stores/wallpaper";
import Drop from "@/components/Drop.vue";
import { onDrop } from "@/utils/onDrop";
import { VuePaginatedAntComposable } from "@/utils/VuePaginatedAnt";
import { useIntervalFn, useDocumentVisibility, useIdle } from "@vueuse/core";
import { computed, ref, watch } from "vue";

const selectedCategories = ref<string[][]>([]);
const selectedType = computed(() => {
  const filter = selectedCategories.value
    .filter((category) => category[0] === "type")
    .map((category) => category[1]);
  if (filter.length === 0) {
    return undefined;
  }
  if (filter[0] === undefined) {
    return undefined;
  }
  return filter;
});
const selectedStatus = computed(() => {
  const filter = selectedCategories.value
    .filter((category) => category[0] === "status")
    .map((category) => category[1]);
  if (filter.length === 0) {
    return undefined;
  }
  if (filter[0] === undefined) {
    return undefined;
  }
  return filter;
});

async function dataFunction(
  search: string,
  sort: string,
  page: number,
  pageSize: number,
) {
  const params = new URLSearchParams();
  params.append("search", search);
  params.append("sort", sort);
  params.append("page", page.toString());
  params.append("limit", pageSize.toString());

  if (selectedType.value) {
    selectedType.value.forEach((type) => {
      params.append("type", type);
    });
  }
  if (selectedStatus.value) {
    selectedStatus.value.forEach((status) => {
      params.append("status", status);
    });
  }

  const response = await fetchWallpapersFromApi(params);

  return {
    data: response.results,
    pagination: {
      total: response.total,
      pageSize: response.limit,
      current: response.page,
    },
  };
}

const {
  loading,
  pagination,
  data,
  search,
  pageSize,
  page,
  debouncedRefreshListView,
} = VuePaginatedAntComposable<Wallpaper>(dataFunction);

const categories = [
  {
    label: "Status of processing",
    value: "status",
    children: [
      {
        label: "Ready",
        value: "1",
      },
      {
        label: "Uploading",
        value: "2",
      },
      {
        label: "Processing",
        value: "3",
      },
      {
        label: "Error",
        value: "4",
      },
    ],
  },
  {
    label: "Type of wallpaper",
    value: "type",
    children: [
      {
        label: "Generic",
        value: "1",
      },
      {
        label: "Time based",
        value: "2",
      },
    ],
  },
];

watch(
  selectedCategories,
  () => {
    debouncedRefreshListView();
  },
  { deep: true },
);

// Auto refresh the list view every 10 seconds when the tab is visible and the user is not idle
const visibility = useDocumentVisibility();
const idle = useIdle(1000 * 60);
useIntervalFn(() => {
  if (visibility.value === "visible" && !idle.idle) {
    debouncedRefreshListView();
  }
}, 1000 * 10);
</script>

<template>
  <Drop text="Drop your pictures here" @drop="onDrop"></Drop>
  <h3 class="text-center text-xl w-full">
    Get your dynamic wallpapers from here:
    <a
      class="underline text-emerald-600"
      href="https://dynamicwallpaper.club/gallery"
      rel="noreferrer"
      target="_blank"
      >dynamicwallpaper.club</a
    >
  </h3>
  <a-divider></a-divider>
  <a-flex justify="center">
    <a-input-search
      v-model:value="search"
      placeholder="Looking for something?"
      style="width: 50%"
    />
  </a-flex>
  <a-divider></a-divider>
  <a-flex justify="center">
    <a-cascader
      v-model:value="selectedCategories"
      style="width: 25%"
      multiple
      max-tag-count="responsive"
      :options="categories"
      placeholder="Select categories"
    ></a-cascader>
  </a-flex>
  <a-divider></a-divider>
  <a-list
    :data-source="data"
    :grid="{ gutter: 16, xs: 1, sm: 1, md: 2, lg: 2, xl: 3, xxl: 4 }"
    :loading="loading"
  >
    <template #renderItem="{ item }">
      <a-list-item>
        <WallpaperPreviewCard :wallpaper="item"></WallpaperPreviewCard>
      </a-list-item>
    </template>
  </a-list>
  <a-flex justify="center">
    <a-pagination
      v-model:current="page"
      v-model:pageSize="pageSize"
      :loading="loading"
      :show-total="
        (total: number, range: number[]) =>
          `${range[0]}-${range[1]} of ${total} items`
      "
      :total="pagination.total"
      hide-on-single-page
    ></a-pagination>
  </a-flex>
</template>
