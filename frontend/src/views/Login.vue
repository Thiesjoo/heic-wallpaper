<script setup lang="ts">
import { useRouter } from "vue-router";
import auth from "@/auth";

const router = useRouter();

async function start() {
  try {
    await auth.startAuthentication();
    router.push("account");
  } catch (e) {}
}

start();
</script>

<template>
  <div
    class="min-h-full flex flex-col items-center justify-center pb-8 px-4 sm:px-6 lg:px-8"
  >
    <div class="max-w-s">Please wait, opening the popup dialog!</div>

    <button
      @click="start"
      class="mt-5 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
    >
      Click here to reopen the dialog
    </button>
  </div>
</template>

<style>
.v-enter-from,
.v-leave-to {
  opacity: 0;
}

.v-enter-active {
  animation: bounce-in 0.5s;
  transition: opacity 0.4s ease;
}

.v-leave-active {
  animation: bounce-in 0.5s reverse;
  transition: opacity 0.4s ease;
}

@keyframes bounce-in {
  0% {
    transform: scale(0);
  }

  100% {
    transform: scale(1);
  }
}
</style>
