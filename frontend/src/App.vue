<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
</script>

<template>
    <header>
        <div
            class="w-full text-right p-3 font-bolder"
            v-if="userStore.loggedIn"
        >
            Logged in as: {{ userStore?.user?.name }} ({{
                userStore?.user?.email
            }})
        </div>
        <div class="wrapper">
            <nav>
                <RouterLink to="/">Home</RouterLink>
                <RouterLink to="/account" v-if="userStore.loggedIn"
                    >Account</RouterLink
                >
            </nav>
        </div>
    </header>

    <main class="flex flex-col items-center justify-center w-full pt-6">
        <Suspense>
            <RouterView />
            <template #fallback> Loading... </template>
        </Suspense>
    </main>
</template>

<style scoped>
header {
    line-height: 1.5;
    max-height: 100vh;
}

nav {
    width: 100%;
    font-size: 12px;
    text-align: center;
    margin-top: 2rem;
}

nav a.router-link-exact-active {
    color: var(--color-text);
}

nav a.router-link-exact-active:hover {
    background-color: transparent;
}

nav a {
    display: inline-block;
    padding: 0 1rem;
    border-left: 1px solid var(--color-border);
}

nav a:first-of-type {
    border: 0;
}
</style>
