import axios from 'axios'

const BASE_URL = 'http://127.0.0.1:8000/api/v1'

const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' }
})

// Get crowd predictions
export const getPredictions = async (payload) => {
  const response = await api.post('/predict', payload)
  return response.data
}

// Get current weather
export const getCurrentWeather = async (city) => {
  const response = await api.get(`/weather/current/${city}`)
  return response.data
}

export const getCityTransport = async (city) => {
  const response = await api.get(`/city/transport/${city}`)
  return response.data
}