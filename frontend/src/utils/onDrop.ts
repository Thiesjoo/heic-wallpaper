import { useToast } from "vue-toastification";
import axios from "axios";
import { useWallpaperStore } from "@/stores/wallpaper";

const toast = useToast();
const allowedTypes = [
  "image/jpeg",
  "image/png",
  "image/gif",
  "image/heif",
  "image/heic",
];

export async function onDrop(file: File) {
  let type = file.type;
  if (!allowedTypes.includes(file.type)) {
    if (file.name.endsWith(".heic") || file.name.endsWith(".heif")) {
      console.warn("No type for: ", file);
      type = "image/heic";
    } else {
      console.warn(file);
      toast.error("Invalid file type.");
      return;
    }
  }

  if (file.size > 100 * 1024 * 1024) {
    toast.error("File size must be less than 50MB.");
    return;
  }

  const presignedURLResult = await fetch("/api/upload", {
    method: "POST",
    body: JSON.stringify({
      name: file.name,
      type: type,
    }),
    headers: {
      "Content-Type": "application/json",
    },
  }).then((res) => res.json());

  if (presignedURLResult.error) {
    console.error(presignedURLResult);
    toast.error("Error uploading file.");
    return;
  }

  const { fields, url } = presignedURLResult.data;

  const progressToast = toast.info("Uploading file: 0%", {
    timeout: 0,
    closeOnClick: false,
  });

  const formData = new FormData();
  for (const key in fields) {
    formData.append(key, fields[key]);
  }
  formData.append("file", file);

  const fileUploadResult = await axios.post(url, formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
    onUploadProgress: function (progressEvent) {
      const percent = progressEvent.total
        ? Math.round((progressEvent.loaded / progressEvent.total) * 100)
        : 0;
      toast.update(progressToast, { content: `Uploading file: ${percent}%` });
    },
  });
  toast.dismiss(progressToast);
  if (fileUploadResult.status !== 204) {
    toast.error("Error uploading file.");
    return;
  }

  const { key, uid } = presignedURLResult;
  const completeResult = await axios.post("/api/upload/complete", {
    key: key,
    uid: uid,
  });

  if (completeResult.status !== 202) {
    toast.error("Error processing file.");
    return;
  }

  toast.success("File uploaded successfully.");
  const wallpaperStore = useWallpaperStore();
  setTimeout(() => {
    wallpaperStore.fetchWallpapers();
  }, 2000);
}

export function startManualUpload() {
  const input = document.createElement("input");
  input.type = "file";
  input.accept = "image/*,image/heic,image/heif";
  input.onchange = (e) => {
    const files = (e.target as HTMLInputElement).files;
    if (files) {
      const file = files[0];
      onDrop(file);
    }
  };
  input.click();
}
