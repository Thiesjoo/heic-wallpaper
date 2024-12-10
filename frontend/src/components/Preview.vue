<script setup lang="ts">
const props = defineProps<{
  url: string;
  size: number;
}>();

const width = props.size;
const height = (props.size * 3) / 4;
</script>

<template>
  <div
    :style="{
      width: `${width}rem`,
      height: `${height}rem`,
    }"
    class="flex-col flex justify-center align-center"
  >
    <img :src="url" class="w-full max-h-[60%]" style="object-fit: cover" />
    <slot></slot>
  </div>
</template>

<style scoped></style>
