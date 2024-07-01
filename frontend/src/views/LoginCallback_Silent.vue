<template>Please wait, redirecting you from silent!</template>
<script lang="ts">
import { defineComponent } from "vue";

import { silentCallback } from "@/auth/oidc";

export default defineComponent({
	mounted() {
		silentCallback();
	},
});
</script>
