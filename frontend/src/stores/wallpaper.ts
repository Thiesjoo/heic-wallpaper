import { ref, computed } from "vue";
import { defineStore } from "pinia";

export type Wallpaper = {
	error: string | null;
	id: string;
	location: string;
	name: string;
	pending: boolean;
	preview_url: string;
	status: number;
};

export enum WallpaperStatus {
    

export const useWallpaperStore = defineStore("", () => {
	// This store should manage all available wallpapers
	const wallpapers = ref<Wallpaper[]>([]);

	// Fetch wallpapers from backend
	const fetchWallpapers = async () => {
		const res = await fetch("/api/wallpapers");
		const data = await res.json();
		wallpapers.value = data;
	};

	// Fetch wallpapers on store creation
	fetchWallpapers();

	// Return wallpapers and fetch function
	return {
		wallpapers: computed(() => wallpapers.value),
		fetchWallpapers,
	};
});
