<script lang="ts" setup>
import {type Wallpaper, WallpaperStatus} from '@/stores/wallpaper'
import {computed} from 'vue'
import {useRouter} from "vue-router";

const props = defineProps<{
    wallpaper: Wallpaper
}>()

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
const router = useRouter();


function click() {
    if (isError.value || isLoading.value) {
        return
    }
    router.push(`/wallpaper/${wallpaper.id}`)
}
</script>

<template>
    <a-card :hoverable="!isLoading&&!isError" :loading="isLoading" :style="{
        cursor: 'pointer',
        width: '350px',
    }" :title="wallpaper.name" @click="click">
        <template #cover>
           <span v-if="isError" class="w-full text-center font-bold">
              This wallpaper is broken
            </span>
            <img
                    v-else-if="!isLoading"
                    :src="wallpaper.preview_url"
                    :style="{
                        height: '200px',
                        objectFit: 'cover',
                    }"
            />
        </template>
        <a-card-meta description="Created by ..., on ...">
        </a-card-meta>
    </a-card>
</template>

<style scoped>

</style>
