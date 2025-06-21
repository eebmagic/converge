import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { InputText } from 'primereact/inputtext';
import { Button } from 'primereact/button';
import { Card } from 'primereact/card';
import { Toast } from 'primereact/toast';

import api from '../helpers/api';

function JoinGame({ user }) {
    const [keyPhrase, setKeyPhrase] = useState('');
    const [loading, setLoading] = useState(false);
    const [joining, setJoining] = useState(false);
    const toast = useRef(null);
    const navigate = useNavigate();

    const showToast = (severity, summary, detail) => {
        toast.current.show({
            severity: severity,
            summary: summary,
            detail: detail,
            life: 3000
        });
    };

    const handleJoinByKeyPhrase = async () => {
        if (!keyPhrase.trim()) {
            showToast('warn', 'Warning', 'Please enter a key phrase');
            return;
        }

        try {
            setJoining(true);
            // Find the game by key phrase
            const result = await api.joinGame(keyPhrase, user.provider_id);
            
            if (result.error) {
                showToast('error', 'Error', result.error);
                return;
            }

            setJoining(false);
            showToast('success', 'Success', 'Successfully joined the game!');
            navigate(`/usergame/${result._id['$oid']}`);
        } catch (error) {
            console.error('Error joining game:', error);
            showToast('error', 'Error', 'Failed to join game');
        } finally {
            setJoining(false);
        }
    };

    const handleJoinGame = async (gameId) => {
        try {
            const result = await api.joinGame(gameId, user.provider_id);
            
            if (result.error) {
                showToast('error', 'Error', result.error);
                return;
            }

            showToast('success', 'Success', 'Successfully joined the game!');
            navigate(`/usergame/${gameId}`);
        } catch (error) {
            console.error('Error joining game:', error);
            showToast('error', 'Error', 'Failed to join game');
        }
    };

    return (
        <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
            <Toast ref={toast} />
            
            <Card title="Join a Game" style={{ marginBottom: '20px' }}>
                <div style={{ marginBottom: '20px' }}>
                    <h3>Join by Key Phrase</h3>
                    <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                        <InputText
                            value={keyPhrase}
                            onChange={(e) => setKeyPhrase(e.target.value)}
                            placeholder="Enter game key phrase"
                            style={{ flex: 1 }}
                            onKeyPress={(e) => e.key === 'Enter' && handleJoinByKeyPhrase()}
                        />
                        <Button
                            label="Join"
                            icon="pi pi-sign-in"
                            onClick={handleJoinByKeyPhrase}
                            loading={joining}
                            disabled={!keyPhrase.trim()}
                        />
                    </div>
                </div>
            </Card>
        </div>
    );
}

export default JoinGame; 