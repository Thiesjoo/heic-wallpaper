import {defineStore} from 'pinia'
import {computed, ref} from 'vue'
import auth from "@/auth"
import type {User, UserFromAPI, UserSettings} from '@/utils/types'
import { useToast } from 'vue-toastification'

export const useUserStore = defineStore('user', () => {
    const user = ref<User | null>(null)
    const loading = ref<boolean>(false);

    async function refreshUserInfo() {
        loading.value = true;
        try {
            await getUserData((await auth.getUser(true)) || undefined);
        } catch (e) {
            reset()
        }
        loading.value = false;
    }

    async function getUserData(cachedUser?: UserFromAPI) {
        loading.value = true;
        try {
            console.log("Getting user data", cachedUser ? "cached" : "");
            user.value = cachedUser || (await auth.getUser()) || null
        } catch (e: any) {
            console.error(e);
        }
        loading.value = false;
    }


    async function updateWallpaper(newUID: string) {
        loading.value = true;

        const myHeaders = new Headers()
        myHeaders.append('pragma', 'no-cache')
        myHeaders.append('cache-control', 'no-cache')
        myHeaders.append('content-type', 'application/json')

        const token = await auth.getToken();
        if (!token) {
            throw new Error("No token found");
        }

        const fetchConfig = {
            method: 'PATCH',
            headers: myHeaders,
            credentials: 'include',
            body: JSON.stringify({
                wallpaper_uid: newUID,
                token: token
            }),
        } satisfies RequestInit
        const toast = useToast();

        fetch('/api/user/set', fetchConfig)
            .then((x) => {
                if (x.status != 200) {
                    throw new Error(x.statusText)
                }

                return x.json()
            })
            .then(function (response) {
                toast.success("Wallpaper updated successfully!")
                console.log(response)
            })
            .catch((x) => {
                toast.error("Failed to update wallpaper, see console for more info.")
                console.error(x)
            })

        loading.value = false;
    }

    function reset(logout = false) {
        loading.value = true;
        user.value = null;
        if (logout) {
            auth.logout()
        }
        loading.value = false;
    }


    return {
        loading,
        user: computed(() => user.value),
        loggedIn: computed(() => user.value !== null),
        updateWallpaper,
        getUserData,
        refreshUserInfo,
        reset
    }
})


export function enableAuth() {
    const store = useUserStore();

    const authedCallback = (user: UserFromAPI) => {
        store.getUserData(user);
    };
    const unauthedCallback = () => {
        store.reset()
    };
    auth.registerCallbacks(authedCallback, unauthedCallback);
}