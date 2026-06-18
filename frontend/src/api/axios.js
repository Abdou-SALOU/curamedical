import axios from 'axios'

const api = axios.create({
    baseURL: '',
    headers: { 'Content-Type': 'application/json' },
})

// Injecte le token JWT automatiquement dans chaque requête
api.interceptors.request.use(config => {
    const token = localStorage.getItem('access_token')
    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }
    return config
})

// Si 401 → refresh automatique du token
// Ne jamais intercepter les erreurs venant des endpoints d'auth eux-mêmes
const AUTH_URLS = ['/api/token/', '/api/token/refresh/', '/api/users/register/']

api.interceptors.response.use(
    response => response,
    async error => {
        const original = error.config
        const isAuthUrl = AUTH_URLS.some(u => original.url?.includes(u))

        if (error.response?.status === 401 && !original._retry && !isAuthUrl) {
            original._retry = true
            try {
                const refresh = localStorage.getItem('refresh_token')
                if (!refresh) throw new Error('no refresh token')
                const res = await axios.post('/api/token/refresh/', { refresh })
                localStorage.setItem('access_token', res.data.access)
                // ROTATE_REFRESH_TOKENS est activé côté backend : un nouveau refresh est renvoyé
                if (res.data.refresh) localStorage.setItem('refresh_token', res.data.refresh)
                original.headers.Authorization = `Bearer ${res.data.access}`
                return api(original)
            } catch {
                localStorage.clear()
                window.location.href = '/login'
            }
        }
        return Promise.reject(error)
    }
)

export default api
