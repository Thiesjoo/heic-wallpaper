<template>
  <div class='vue-full-screen-file-drop' :class='classes'>
    <slot>
      <div class='vue-full-screen-file-drop__content'>
        {{ text }}
      </div>
    </slot>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { onUnmounted } from 'vue'
import { computed } from 'vue'
import { ref } from 'vue'

interface IProps {
  text: string
}

defineProps<IProps>()

const $emit = defineEmits<{
  (e: 'drop', files: File): void
}>()

const visible = ref(false)
const lastTarget = ref(null)

const classes = computed(() => {
  return {
    'vue-full-screen-file-drop--visible': visible.value,
  }
})

function onDragEnter(e: any) {
  lastTarget.value = e.target as any
  visible.value = true
}
function onDragLeave(e: any) {
  if (e.target === lastTarget.value) {
    visible.value = false
  }
}
function onDragOver(e: any) {
  e.preventDefault()
}
function onDrop(e: any) {
  e.preventDefault()
  visible.value = false
  const files: File[] = Array.from(e.dataTransfer.files)
  if (files.length) {
    files.forEach((file) => {
      $emit('drop', file)
    })
  }
}

onMounted(() => {
  window.addEventListener('dragenter', onDragEnter);
  window.addEventListener('dragleave', onDragLeave);
  window.addEventListener('dragover', onDragOver);
  window.addEventListener('drop', onDrop);
})

onUnmounted(() => {
  window.removeEventListener('dragenter', onDragEnter);
  window.removeEventListener('dragleave', onDragLeave);
  window.removeEventListener('dragover', onDragOver);
  window.removeEventListener('drop', onDrop);
})

</script>

<style lang='css'>
  .vue-full-screen-file-drop {
    position: fixed;
    top: 0;
    left: 0;
    z-index: 10000;
    width: 100%;
    height: 100%;
    background-color: rgba(0,0,0,0.4);
    visibility: hidden;
    opacity: 0;
    transition: visibility 200ms, opacity 200ms;
  }

  .vue-full-screen-file-drop--visible {
    opacity: 1;
    visibility: visible;
  }

  .vue-full-screen-file-drop__content {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    height: 100%;
    color: #fff;
    font-size: 4em;
  }

  .vue-full-screen-file-drop__content:before {
    border: 5px dashed #fff;
    content: "";
    bottom: 60px;
    left: 60px;
    position: absolute;
    right: 60px;
    top: 60px;
  }
</style>