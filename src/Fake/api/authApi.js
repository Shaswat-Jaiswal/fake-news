import axios from "axios";

const API = axios.create({
  baseURL: "https://fake-news-nrdn.onrender.com/api/auth",
  withCredentials: true, // include cookies if backend sets them
});

// ✅ Request Interceptor (YAHI ADD HOGA)
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

export const signupUser = (userData) => {
  return API.post("/signup", userData);
};

export const loginUser = (credentials) => {
  return API.post("/login", credentials);
};

export default API;
