declare global {
  interface Window {
    fetch(
      input: RequestInfo | URL,
      init?: RequestInit,
      throwError?: boolean,
    ): Promise<Response>;
  }
}
import "./assets/main.css";

import { createApp } from "vue";
import { createPinia } from "pinia";
//@ts-ignore
import DropZone from "dropzone-vue";

import Antd from "ant-design-vue";
import "ant-design-vue/dist/reset.css";

import App from "./App.vue";
import router from "./router";

import "dropzone-vue/dist/dropzone-vue.common.css";
import { enableAuth, useUserStore } from "./stores/user";
import Toast from "vue-toastification";
import "vue-toastification/dist/index.css";

const app = createApp(App);

app.use(DropZone);
app.use(Toast);
app.use(createPinia());
app.use(router);
app.use(Antd);

app.mount("#app");

enableAuth();
const store = useUserStore();
(async () => {
  await store.getUserData();
})();
