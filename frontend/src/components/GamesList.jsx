import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

import api from '../helpers/api';

function GamesList({ user }) {
    const [games, setGames] = useState([]);

    useEffect(() => {
        const fetchGames = async () => {
            const result = await api.getGames(user.provider_id);
            setGames(result.games);
        };
        fetchGames();
    }, [user]);

    return (
        <div>
            <h1>Games List:</h1>
            {games && games.map((game) => (
                <div key={game._id['$oid']}>
                    <h2>{game.key_phrase}</h2>
                    <p>player 1: {game.player1}</p>
                    <p>player 2: {game.player2}</p>
                    <p>status: {game.game_state}</p>
                    <Link to={`/usergame/${game._id['$oid']}`}>View Game</Link>
                </div>
            ))}
        </div>
    );
}

export default GamesList;