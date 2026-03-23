import axios from 'axios'

const BASE_URL = 'http://127.0.0.1:8000/api/v1'

const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' }
})

export const getPredictions     = async (payload) => (await api.post('/predict', payload)).data
export const getCurrentWeather  = async (city)    => (await api.get(`/weather/current/${city}`)).data
export const getCityTransport   = async (city)    => (await api.get(`/city/transport/${city}`)).data
export const getHolidayImpact   = async (dt)      => (await api.get(`/holiday/impact`, { params: { datetime_str: dt } })).data