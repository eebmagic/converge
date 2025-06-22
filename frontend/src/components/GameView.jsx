import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import api from '../helpers/api';

function GameView({ user }) {
    const { gameId } = useParams();

    const [game, setGame] = useState(null);
    const [word, setWord] = useState('');
    const sendMove = async (word) => {
        const result = await api.addMove(gameId, user.provider_id, word);
        setGame(result);
    }

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

    const submitWidget = () => {
        if (!game) return;
        if (game.game_state !== 'in_progress') return;

        if (game.player1_moves.length > game.player2_moves.length) {
            return <p>Waiting for <b>{game.player2?.name}</b> to submit their move</p>;
        }

        return (
            <div>
                <h2>Submit Widget</h2>
                <input type="text" placeholder="Enter your word" onChange={(e) => setWord(e.target.value)} />
                <button onClick={() => sendMove(word)}>Submit</button>
            </div>
        );
    }

    const historyWidget = () => {
        if (!game) return;
        if (game.game_state !== 'in_progress') return;

        if (game.player1_moves.length === 0) {
            return <p>No moves yet</p>;
        };

        return (
            <div>
                {game.player1_moves.map(word => {
                    return <p>{word}</p>
                })}
                {game.player2_moves.map(word => {
                    return <p>{word}</p>
                })}
            </div>
        );
    }

    return (
        <div>
            <h1>Game View:</h1>
            {game && (
                <div key={game._id}>
                    <h2>{game.key_phrase}</h2>
                    <p>player 1: {game.player1?.name}</p>
                    <img src={game.player1?.details?.picture} alt="player 1 avatar" />
                    <p>player 2: {game.player2?.name}</p>
                    <img src={game.player2?.details?.picture} alt="player 2 avatar" />
                    <p>status: {game.game_state}</p>

                    {submitWidget()}

                    <div>
                        <h2>Game History</h2>
                        {historyWidget()}
                    </div>
                </div>
            )}
        </div>
    );
}

export default GameView;