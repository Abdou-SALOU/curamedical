import api from './axios'

export const login = async (username, password) => {
    const res = await api.post('/api/token/', {
        username,
        password,
    })
    return res.data
}

export const getMe = () => api.get('/api/users/me/')
export const refreshToken = (refresh) => api.post('/api/token/refresh/', { refresh })
