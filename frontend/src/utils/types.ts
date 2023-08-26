export type User = {
    name: {
        first: string
        last: string
    }
    email: string
    settings: UserSettings
}

export type UserSettings = {
    backgroundURL: string
    showSeconds: boolean
    showDate: boolean
    showVersion: boolean
    showFavorites: boolean
    widgetsAvailable: unknown[]
}

export type UserFromAPI = Omit<User, 'settings'> & {
    settings: Omit<User['settings'], 'widgets' | 'favorites'>
}
