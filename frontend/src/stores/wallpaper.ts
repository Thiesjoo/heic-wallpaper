import { defineStore } from "pinia";
import { useToast } from "vue-toastification";

export type Wallpaper = {
  id: string;
  uid: string;

  name: string;

  status: WallpaperStatus;
  type: WallpaperType;

  date_created: string;
  date_modified: string;

  owner: {
    first_name: string;
    last_name: string;
  };

  preview_url: string;
};
export type WallpaperWithDetails = Wallpaper & {
  data: { i: number; t: number }[] | undefined;
};

export type PaginatedResponse<T> = {
  results: T[];
  total: number;
  page: number;
  limit: number;
};

export function getUserWallpaperURL(wallpaper: Wallpaper) {
  return `${window.location.origin}/wallpaper/${wallpaper.id}`;
}

export function getApiWallpaperURL(wallpaper: Wallpaper) {
  return `${window.location.origin}/api/wallpaper/${wallpaper.id}`;
}

export function getRouterWallpaperURL(wallpaper: Wallpaper) {
  return `/wallpaper/${wallpaper.id}`;
}

export enum WallpaperStatus {
  READY = 1,
  UPLOADING = 2,
  PROCESSING = 3,
  ERROR = 4,
}

export enum WallpaperType {
  GENERIC = 1,
  TIME_BASED = 2,
}

export async function fetchWallpapersFromApi(
  params: URLSearchParams,
): Promise<PaginatedResponse<Wallpaper[]>> {
  const res = await fetch(`/api/wallpapers/?${params}`);
  return await res.json();
}

export const useWallpaperStore = defineStore("wallpapers", () => {
  const fetchSpecificWallpaper = async (
    id: string,
  ): Promise<WallpaperWithDetails> => {
    try {
      const res = await fetch(`/api/wallpapers/${id}/`);
      if (res.status !== 200) {
        throw new Error("Wallpaper is not available here");
      }
      return await res.json();
    } catch (e: any) {
      const toast = useToast();
      toast.error("Failed to fetch wallpaper");
      throw e;
    }
  };

  async function getWallpaperById(id: string) {
    return await fetchSpecificWallpaper(id);
  }

  return {
    getWallpaperById,
  };
});
