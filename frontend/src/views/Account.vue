<script setup lang="ts">

import {useUserStore} from "@/stores/user";

const userStore = useUserStore();
</script>
<template>
  <div v-if="userStore.loggedIn">
    <h1>Hi! You are:</h1>
    <span>{{ userStore.user.name }} with email: {{ userStore.user.email }}</span>
  </div>
</template>
