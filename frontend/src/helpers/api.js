const API_BASE = process.env.REACT_APP_API_BASE;
if (!API_BASE) {
    throw new Error('API_BASE is not set. Set in frontend/.env');
}

const createUser = async (userData) => {
    const payload = {
        provider_id: userData.sub,
        provider: 'google',
        name: userData.name,
        email: userData.email,
        details: userData,
    }
    const response = await fetch(`${API_BASE}/users`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
    });

    if (!response.ok) {
        throw new Error('Failed to create user');
    }

    return response.json();
};

const getUser = async (userDetails) => {
    const url = `${API_BASE}/users/${userDetails.sub}`;
    const response = await fetch(url, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    });

    if (!response.ok && response.status === 404) {
        // Fallback to creating a user if the current user is not found
        return createUser(userDetails);
    }

    return response.json();
};

const updateUser = async (userId, changes) => {
    const response = await fetch(`${API_BASE}/users/${userId}`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(changes),
    });

    return response.json();
};

const createGame = async (userId) => {
    const response = await fetch(`${API_BASE}/games`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Custom-Data': JSON.stringify({ user: userId }),
        },
    });

    return response.json();
};

const getGames = async (userId) => {
    const response = await fetch(`${API_BASE}/games`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-Custom-Data': JSON.stringify({ user: userId }),
        },
    });

    return response.json();
};

const getGame = async (gameId, userId) => {
    const response = await fetch(`${API_BASE}/games/${gameId}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-Custom-Data': JSON.stringify({ user: userId }),
        },
    });

    return response.json();
};

module.exports = {
    createUser,
    getUser,
    updateUser,
    createGame,
    getGames,
    getGame,
};