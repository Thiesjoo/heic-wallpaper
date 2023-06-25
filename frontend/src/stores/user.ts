import {defineStore} from "pinia";
import {computed, ref} from "vue";

export type User = {
    email: string;
    uid: string;
    passageID: string;
    name: string;
}

export const useUserStore = defineStore("user", () => {

    const user = ref<User | null>(null);
    fetch("https://auth.thies.dev/api/users/me", {
        credentials: "include",
        //@ts-ignore
    }, false)
        .then((res) => res.json())
        .then((data) => {
            user.value = data;
        })

    const loggedIn = computed(() => user.value !== null);

    return {
        user: computed(() => user.value),
        loggedIn,
    }
})