declare global {
    interface Window {
        fetch(
            input: RequestInfo | URL,
            init?: RequestInit,
            throwError?: boolean
        ): Promise<Response>
    }
}
import './utils/401'

import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
//@ts-ignore
import DropZone from 'dropzone-vue'

import App from './App.vue'
import router from './router'

import 'dropzone-vue/dist/dropzone-vue.common.css'

const app = createApp(App)

app.use(DropZone)
app.use(createPinia())
app.use(router)

app.mount('#app')
