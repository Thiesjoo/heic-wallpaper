import {ref, computed} from "vue";
import {defineStore} from "pinia";

export type Wallpaper = {
    error: string | null;
    id: string;
    location: string;
    name: string;
    preview_url: string;
    created_by: string;
    status: WallpaperStatus;
    type: WallpaperType;
};

export type WallpaperWithDetails = Wallpaper & {
    data: { i: number, t: number }[] | undefined
}

export enum WallpaperStatus {
    READY = 1,
    PROCESSING = 2,
    ERROR = 3,
    DELETED = 4,
}

export enum WallpaperType {
    NORMAL = 1,
    HEIC = 2,
    ANIMATED = 3,
}

export const useWallpaperStore = defineStore("wallpapers", () => {
    // This store should manage all available wallpapers
    const wallpapers = ref<Wallpaper[]>([]);
    const lastError = ref<string>("");

    // Fetch wallpapers from backend
    const fetchWallpapers = async (): Promise<Wallpaper[]> => {
        try {
            const res = await fetch("/api/wallpapers");
            const data = await res.json();
            wallpapers.value = data;
            return data;
        } catch (e: any) {
            lastError.value = e?.message || "Unknown error";
        }
        return [];
    };

    const fetchSpecificWallpaper = async (id: string): Promise<WallpaperWithDetails> => {
        try {
            const res = await fetch(`/api/wallpaper/${id}/details`);
            const data = await res.json();
            return data;
        } catch (e: any) {
            lastError.value = e?.message || "Unknown error";
            throw e;
        }
    }

    // Fetch wallpapers on store creation
    fetchWallpapers();

    // Fetch wallpapers every 10 seconds
    setInterval(fetchWallpapers, 10000);


    async function getWallpaperById(id: string) {
        return await fetchSpecificWallpaper(id);
    }

    // Return wallpapers and fetch function
    return {
        wallpapers: computed(() => wallpapers.value),
        fetchWallpapers,
        getWallpaperById,
        lastError: computed(() => lastError.value),
    };
});
