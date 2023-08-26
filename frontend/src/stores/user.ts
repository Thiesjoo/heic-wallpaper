import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import auth from "@/auth"
import type { User, UserFromAPI } from '@/utils/types'

export const useUserStore = defineStore('user', () => {
    const user = ref<User | null>(null)
    const loggedIn = computed(() => user.value !== null)



    async function refreshUserInfo() {
        await getUserData((await auth.getUser(true)) || undefined);
    },

    async function getUserData(cachedUser?: UserFromAPI) {
        try {
            console.log("Getting user data");
            user = cachedUser || (await auth.getUser());
            if (!user) {
                loading.userdata = false;
                user = null;
                return;
            }


        } catch (e: any) {
            console.error(e);
        }
    },


    function getSettings(): Promise<UserSettings> {}

    function updateWallpaper(newURL: string) {
        const myHeaders = new Headers()
        myHeaders.append('pragma', 'no-cache')
        myHeaders.append('cache-control', 'no-cache')
        myHeaders.append('content-type', 'application/json')

        const fetchConfig = {
            method: 'PATCH',
            headers: myHeaders,
            credentials: 'include',
            body: JSON.stringify({
                backgroundURL: newURL,
            }),
        } satisfies RequestInit

        fetch('https://auth.thies.dev/api/settings/me', fetchConfig)
            .then((x) => {
                if (x.status != 200) {
                    throw new Error(x.statusText)
                }

                return x.json()
            })
            .then(function (response) {
                console.log(response)
            })
            .catch((x) => {
                console.error(x)
            })
    }

    return {
        user: computed(() => user.value),
        loggedIn,
        updateWallpaper,
        getSettings,
    }
})
