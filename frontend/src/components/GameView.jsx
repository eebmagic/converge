import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import api from '../helpers/api';

function GameView({ user }) {
    const { gameId } = useParams();

    const [game, setGame] = useState(null);
    const [word, setWord] = useState('');
    const sendMove = async (word) => {
        const result = await api.addMove(gameId, user.provider_id, word);
        if (result.error) {
            alert(result.error);
            return;
        }
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

        const minLength = Math.min(game.player1_moves.length, game.player2_moves.length);
        const historyData = [];

        for (let i = 0; i < minLength; i++) {
            historyData.push({
                round: i + 1,
                player1Move: game.player1_moves[i],
                player2Move: game.player2_moves[i]
            });
        }

        historyData.reverse();

        return (
            <DataTable value={historyData} tableStyle={{ minWidth: '50rem' }}>
                <Column field="round" header="Round"></Column>
                <Column field="player1Move" header="Your Moves"></Column>
                <Column field="player2Move" header="Their Moves"></Column>
            </DataTable>
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