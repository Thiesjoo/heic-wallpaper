<script lang="ts" setup>
defineProps<{
  url: string;
}>();
</script>

<template>
  <a-card
    :style="{
      width: `300px`,
    }"
  >
    <template #cover>
      <img
        :src="url"
        :style="{
          height: '200px',
          objectFit: 'cover',
        }"
      />
    </template>
    <template #title>
      <a-flex justify="space-between">
        <slot></slot>
      </a-flex>
    </template>
  </a-card>
</template>

<style scoped></style>
