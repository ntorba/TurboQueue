    const player = new window.Spotify.Player({
        name: 'TurboQueue Biiiiiitch',
        getOAuthToken: cb => { cb(token); },
        volume: 0.5
    });
