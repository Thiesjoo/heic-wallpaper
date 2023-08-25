const originalFetch = window.fetch
window.fetch = async (input: any, init?: any, throwError = true) => {
    const res = await originalFetch(input, init)
    if (res.status === 401 && throwError) {
        // Redirect to login page
        window.location.href = `https://thies.dev/login?next=${window.location.href}`
    }
    return res
}
