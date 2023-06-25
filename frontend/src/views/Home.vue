<script setup lang="ts">
import Wallpaper from "@/components/SingleWallpaper.vue";
import { useWallpaperStore } from "@/stores/wallpaper";

function err(data: {
	files: {
		name: string;
	};
	error: "INVALID_TYPE" | "MAX_FILE" | "MAX_FILE_SIZE";
}) {
	console.error(data);
	alert("1");
}

const wallpaperStore = useWallpaperStore();
function uploaded(file: any) {
	alert("File upload was a success!");
	// notyf.success("File upload was a success!");
	wallpaperStore.fetchWallpapers();
}
</script>

<template>
	<!-- Dropzone -->
	<DropZone
		class="dropzone"
		:autoProcessQueue="true"
		:uploadMultiple="false"
		:parallelUploads="5"
		:acceptedFiles="['heic']"
		:maxFileSize="100000000000000000"
		url="/api/upload"
		@error-add="err"
		@uploaded="uploaded"></DropZone>

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
		<h3 class="text-center text-xl text-emerald-300">All available wallpapers</h3>
		<div id="content" class="w-full h-full flex items-center justify-center flex-wrap">
			<span class="text-red-600 w-full text-center" v-if="wallpaperStore.lastError">{{
				wallpaperStore.lastError
			}}</span>
			<Wallpaper :wallpaper="wallpaper" v-for="wallpaper in wallpaperStore.wallpapers"></Wallpaper>
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
