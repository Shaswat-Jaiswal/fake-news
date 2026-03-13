import axios from "axios";

const API = axios.create({
  baseURL: "https://fake-news-nrdn.onrender.com/api/auth",
  withCredentials: true,
});

// Request Interceptor - Add JWT token
API.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export const analyzeNews = (text) => {
  return API.post("/analyze", { text });
};

export default API;
