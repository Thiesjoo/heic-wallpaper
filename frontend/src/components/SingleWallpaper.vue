<script setup lang="ts">
import type { Wallpaper } from "@/stores/wallpaper";
import Preview from "./Preview.vue";
defineProps<{
	wallpaper: Wallpaper;
}>();
</script>

<template>
	<Preview :url="wallpaper.preview_url">
		<span class="w-full text-center font-bold">Title</span>
		<!-- Show 3 buttons horizontal -->
		<div class="flex flex-row h-16">
			<!-- Copy URL -->
			<button
				class="w-full bg-blue-500 hover:bg-blue-700 text-white font-bold px-4 m-4 rounded"
				onclick="handleCopyClick(this)">
				Copy
			</button>
			<!-- Open button -->
			<button
				class="w-full bg-blue-500 hover:bg-blue-700 text-white font-bold px-4 m-4 rounded"
				onclick="handleOpenClick(this)">
				Open
			</button>

			<!-- Select button -->
			<button
				class="w-full bg-blue-500 hover:bg-blue-700 text-white font-bold px-4 m-4 rounded"
				onclick="handleSetClick(this)">
				Set
			</button>
		</div>
	</Preview>
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
