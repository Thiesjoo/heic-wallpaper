<template>Please wait, redirecting you!</template>
<script lang="ts">
import { defineComponent } from "vue";

import { callback } from "@/auth/oidc";

export default defineComponent({
	mounted() {
		callback();
	},
});
</script>
