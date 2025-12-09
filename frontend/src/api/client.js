/** API client for backend communication */
import axios from 'axios';
import { API_BASE_URL } from '../config';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;

