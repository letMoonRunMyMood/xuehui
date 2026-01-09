import axios from 'axios';

const axiosInstance = axios.create({
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
    },
    withCredentials: true
});

axiosInstance.interceptors.request.use(
    (config) => {
        config.headers['ngrok-skip-browser-warning'] = '1';
        
        if (config.data instanceof FormData) {
            delete config.headers['Content-Type'];
        }
        config.withCredentials = true;
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

export default axiosInstance;