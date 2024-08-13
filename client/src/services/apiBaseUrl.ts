const isProd = import.meta.env.PROD;

const API_BASE_URL = isProd ?
    import.meta.env.VITE_API_BASE_URL_PROD :
    'http://localhost:8000';

export default API_BASE_URL;
