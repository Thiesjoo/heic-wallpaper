<script setup lang="ts">
defineProps<{
	url: string;
}>();
</script>

<template>
	<div class="w-80 h-60 flex-col flex justify-center align-center border p-3 m-3">
		<img :src="url" class="w-full max-h-[60%]" style="object-fit: cover" />
		<slot></slot>
	</div>
</template>

<style scoped></style>
