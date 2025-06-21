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

    const renderGame = (game) => {
        return (
            <div key={game._id['$oid']}>
                <h2>{game.key_phrase}</h2>
                <p>player 1: {game.player1?.name}</p>
                <img src={game.player1?.details?.picture} alt="player 1 avatar" />
                <p>player 2: {game.player2?.name}</p>
                <img src={game.player2?.details?.picture} alt="player 2 avatar" />
                <p>status: {game.game_state}</p>

                <Link to={`/usergame/${game._id['$oid']}`}>View Game</Link>
            </div>
        );
    };

    return (
        <div>
            <h1>Games List:</h1>
            {games && games.map(renderGame)}
        </div>
    );
}

export default GamesList;