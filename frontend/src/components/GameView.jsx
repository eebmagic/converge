import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import api from '../helpers/api';

function GameView({ user }) {
    const { gameId } = useParams();

    const [game, setGame] = useState(null);

    // Pull the game details from the server
    useEffect(() => {
        async function pullGame() {
            const result = await api.getGame(gameId, user.provider_id);
            setGame(result);
        }

        const willPullGame = user && gameId && !game;
        if (willPullGame) {
            pullGame();
        }
    }, [user, gameId, game]);

    return (
        <div>
            <h1>Game View:</h1>
            {game && (
                <div key={game._id}>
                    <h2>{game.key_phrase}</h2>
                    <p>player 1: {game.player1.name}</p>
                    <img src={game.player1.details.picture} alt="player 1 avatar" />
                    <p>player 2: {game.player2.name}</p>
                    <img src={game.player2.details.picture} alt="player 2 avatar" />
                    <p>status: {game.game_state}</p>
                </div>
            )}
        </div>
    );
}

export default GameView;