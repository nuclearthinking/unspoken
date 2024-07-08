export const getBackendUrl = () => {
    const protocol = import.meta.env.VITE_API_PROTOCOL || 'http';
    const host = import.meta.env.VITE_API_HOST || 'localhost';
    const port = import.meta.env.VITE_API_PORT || '8000';
    return `${protocol}://${host}${port ? `:${port}` : ''}`;
}
