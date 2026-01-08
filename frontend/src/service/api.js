import axios from 'axios';

const axiosInstance = axios.create({
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
});

export default axiosInstance;