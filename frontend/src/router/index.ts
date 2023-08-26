import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            name: 'home',
            component: Home,
        },
        {
            path: '/wallpaper/:id',
            name: 'Wallpaper',
            component: () => import('../views/Wallpaper.vue'),
        },
        {
            path: '/account',
            name: 'Account',
            // route level code-splitting
            // this generates a separate chunk (About.[hash].js) for this route
            // which is lazy-loaded when the route is visited.
            component: () => import('../views/Account.vue'),
        },
        {
            path: "/login",
            name: "Login",
            component: () => import("../views/Login.vue")
        },
        {
            path: "/login/callback",
            name: "Login Callback",
            component: () => import("../views/LoginCallback.vue")
        }
    ],
})

export default router
