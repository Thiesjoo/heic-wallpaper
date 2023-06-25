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


    function updateWallpaper(newURL: string) {
        const myHeaders = new Headers();
        myHeaders.append('pragma', 'no-cache');
        myHeaders.append('cache-control', 'no-cache');
        myHeaders.append("content-type", "application/json")

        const fetchConfig  = {
            method: 'PATCH',
            headers: myHeaders,
            credentials: "include",
            body: JSON.stringify({
                backgroundURL: newURL
            })
        } satisfies RequestInit

        fetch("https://auth.thies.dev/api/settings/me", fetchConfig)
            .then(x => {
                if (x.status != 200) {
                    throw new Error(x.statusText)
                }

                return x.json()
            })
            .then(function (response) {
                console.log(response)
            }).catch(x => {
            console.error(x)
        })
    }

    return {
        user: computed(() => user.value),
        loggedIn,
        updateWallpaper
    }
})