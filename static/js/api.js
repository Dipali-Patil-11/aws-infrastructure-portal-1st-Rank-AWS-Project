// API wrapper functions using Fetch API

async function apiGet(endpoint) {
    try {
        const response = await fetch(endpoint, {
            cache: 'no-store',
            headers: {
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache'
            }
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'API Error');
        return data;
    } catch (error) {
        showToast('Error', error.message, 'error');
        throw error;
    }
}

async function apiPost(endpoint, payload) {
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'API Error');
        return data;
    } catch (error) {
        showToast('Error', error.message, 'error');
        throw error;
    }
}

async function apiDelete(endpoint, payload) {
    try {
        const response = await fetch(endpoint, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'API Error');
        return data;
    } catch (error) {
        showToast('Error', error.message, 'error');
        throw error;
    }
}
