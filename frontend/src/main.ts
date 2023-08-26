declare global {
    interface Window {
        fetch(
            input: RequestInfo | URL,
            init?: RequestInit,
            throwError?: boolean
        ): Promise<Response>
    }
}
import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
//@ts-ignore
import DropZone from 'dropzone-vue'

import App from './App.vue'
import router from './router'

import 'dropzone-vue/dist/dropzone-vue.common.css'
import { enableAuth, useUserStore } from './stores/user'

const app = createApp(App)

app.use(DropZone)
app.use(createPinia())
app.use(router)

app.mount('#app')


enableAuth();
const store = useUserStore();
(
    async () => {
        await store.getUserData();
        await store.refreshUserInfo()
    }
)()

