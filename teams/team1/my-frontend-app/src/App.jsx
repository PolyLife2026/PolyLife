import React, { useEffect, useState } from 'react';
import api from './services/api';

function App() {
    const [status, setStatus] = useState('Checking backend...');

    useEffect(() => {
        // Example call to team1 backend (e.g., competitions list)
        api.get('/competitions/')
            .then(response => {
                setStatus('Connected to PolyLife Backend!');
            })
            .catch(error => {
                setStatus('Backend not reachable yet.');
                console.error(error);
            });
    }, []);

    return (
        <div>
            <h1>PolyLife Frontend</h1>
            <p>Backend Status: {status}</p>
        </div>
    );
}

export default App;
