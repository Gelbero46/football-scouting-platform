import axios, { AxiosInstance } from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const API_VERSION = process.env.NEXT_PUBLIC_API_VERSION || 'v1'

class ApiClient {
  private client: AxiosInstance

  constructor(token?: string) {
    console.log("api-client token", token)
    this.client = axios.create({
      baseURL: `${API_URL}/api/${API_VERSION}`,
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
      },
    })

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          if (typeof window !== 'undefined') {
            window.location.href = '/sign-in'
          }
        }
        return Promise.reject(error)
      }
    )
  }

  // Auth endpoints
  auth = {
    getCurrentUser: () => this.client.get('/auth/me'),
    syncUser: () => this.client.post('/auth/sync'),
  }

  // Player endpoints
  players = {
    list: (params?: any) => this.client.get('/players', { params }),
    get: (id: string) => this.client.get(`/players/${id}`),
    create: (data: any) => this.client.post('/players', data),
    update: (id: string, data: any) => this.client.put(`/players/${id}`, data),
    delete: (id: string) => this.client.delete(`/players/${id}`),
    similar: (id: string) => this.client.get(`/players/${id}/similar`),
    stats: () => this.client.get('/players/stats/summary'),
  }

  // Coach endpoints
  coaches = {
    list: (params?: any) => this.client.get('/coaches', { params }),
    get: (id: string) => this.client.get(`/coaches/${id}`),
    create: (data: any) => this.client.post('/coaches', data),
    update: (id: string, data: any) => this.client.put(`/coaches/${id}`, data),
    delete: (id: string) => this.client.delete(`/coaches/${id}`),
    similar: (id: string) => this.client.get(`/coaches/${id}/similar`),
  }

  // Shortlist endpoints
  shortlists = {
    list: (params?: any) => this.client.get('/shortlists', { params }),
    get: (id: string) => this.client.get(`/shortlists/${id}`),
    create: (data: any) => this.client.post('/shortlists', data),
    update: (id: string, data: any) => this.client.put(`/shortlists/${id}`, data),
    delete: (id: string) => this.client.delete(`/shortlists/${id}`),
    addItem: (id: string, data: any) => this.client.post(`/shortlists/${id}/items`, data),
    updateItem: (shortlistId: string, itemId: string, data: any) =>
      this.client.put(`/shortlists/${shortlistId}/items/${itemId}`, data),
    removeItem: (shortlistId: string, itemId: string) =>
      this.client.delete(`/shortlists/${shortlistId}/items/${itemId}`),
  }

  // Report endpoints
  reports = {
    list: (params?: any) => this.client.get('/reports', { params }),
    get: (id: string) => this.client.get(`/reports/${id}`),
    create: (data: any) => this.client.post('/reports', data),
    delete: (id: string) => this.client.delete(`/reports/${id}`),
    download: (id: string) => this.client.get(`/reports/${id}/download`),
  }
}

export default ApiClient