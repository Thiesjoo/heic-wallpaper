<script lang="ts" setup>
import { RouterLink, RouterView, useRoute } from "vue-router";
import { useUserStore } from "@/stores/user";
import { theme } from "ant-design-vue";
import { computed } from "vue";
import { UploadOutlined } from "@ant-design/icons-vue";
import { startManualUpload } from "@/utils/onDrop";

const userStore = useUserStore();

const route = useRoute();
const selectedKeys = computed(() => [route.path]);
const initials = computed(() => {
  return (
    (userStore.user?.name?.first?.charAt(0) || "John") +
    (userStore.user?.name?.last?.charAt(0) || "Doe")
  );
});
</script>

<template>
  <a-config-provider
    :theme="{
      algorithm: theme.darkAlgorithm,
    }"
  >
    <a-layout>
      <a-layout-header :style="{ position: 'fixed', zIndex: 1, width: '100%' }">
        <a-flex justify="space-between">
          <a-flex
            :style="{
              minWidth: '200px',
            }"
          >
            <div class="logo" />
            <a-menu
              v-model:selected-keys="selectedKeys"
              :style="{ lineHeight: '64px', minWidth: '200px' }"
              mode="horizontal"
              theme="dark"
            >
              <a-menu-item key="/">
                <RouterLink to="/">Gallery</RouterLink>
              </a-menu-item>
              <a-menu-item v-if="!userStore.loggedIn" key="/login">
                <RouterLink to="/login">Login</RouterLink>
              </a-menu-item>
            </a-menu>
          </a-flex>

          <a-flex align="center" justify="center">
            <template v-if="userStore.loggedIn">
              <a-button
                size="large"
                type="default"
                @click="startManualUpload"
                title="You can also drop your images anywhere on this page."
              >
                <template #icon>
                  <UploadOutlined />
                </template>
                Upload
              </a-button>
              <a-divider type="vertical" />
              <a-dropdown>
                <a-avatar
                  :size="48"
                  :style="{
                    backgroundColor: '#f56a00',
                    verticalAlign: 'middle',
                  }"
                >
                  {{ initials }}
                </a-avatar>
                <template #overlay>
                  <a-menu>
                    <a-menu-item key="0">
                      <RouterLink to="/account">Account</RouterLink>
                    </a-menu-item>
                    <a-menu-divider />
                    <a-menu-item key="3">
                      <a @click="userStore.reset">Logout</a>
                    </a-menu-item>
                  </a-menu>
                </template>
              </a-dropdown>
            </template>
          </a-flex>
        </a-flex>
      </a-layout-header>
      <a-layout-content
        :style="{
          padding: '0 50px',
          marginTop: '72px',
          minHeight: 'calc(100vh - 72px)',
        }"
      >
        <Suspense>
          <RouterView />
          <template #fallback> Loading...</template>
        </Suspense>
      </a-layout-content>
      <a-layout-footer>
        <a-divider />
        <a-row justify="center">
          <a-col>
            <span>Heic Wallpaper | Created by Thies Nieborg</span>
          </a-col>
        </a-row>
      </a-layout-footer>
    </a-layout>
  </a-config-provider>
</template>

<style scoped></style>
