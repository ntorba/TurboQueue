const getHashParams = () => {
    var hashParams = {};
    var e, r = /([^&;=]+)=?([^&;]*)/g,
        q = window.location.hash.substring(1);
    e = r.exec(q);
    while (e) {
        hashParams[e[1]] = decodeURIComponent(e[2]);
        e = r.exec(q);
    }
    return hashParams;
};

var params = getHashParams();

window.onSpotifyWebPlaybackSDKReady = () => {
    const token = params.access_token;
    localStorage.setItem("tq_oauth_token", token);
    if (params.access_token) {
        // TODO: I need a mobile page with no playback controls that actually works
        console.log("Make a page with no playback controls");
    }
    const player = new window.Spotify.Player({
        name: 'TurboQueue Biiiiiitch',
        getOAuthToken: cb => { cb(token); },
        volume: 0.5
    });

    // Ready
    player.addListener('ready', ({ device_id }) => {
        // DEVICE_ID = device_id;
        localStorage.setItem("tq_oath_current_device_id", device_id);
        console.log('Ready with Device ID', device_id);
    });

    // Not Ready
    player.addListener('not_ready', ({ device_id }) => {
        console.log('Device ID has gone offline', device_id);
    });

    player.addListener('initialization_error', ({ message }) => {
        console.error(message);
    });

    player.addListener('authentication_error', ({ message }) => {
        console.error(message);
    });

    player.addListener('account_error', ({ message }) => {
        console.error(message);
    });

    // player.addListener('player_state_changed', (state => {

    //     if (!state) {
    //         return;
    //     }

    //     // var track = state.track_window.current_track;
    //     // var paused = state.paused;
    //     fetch(
    //         'http://localhost:5000/set_now_playing',
    //         {
    //             method: 'POST',
    //             headers: {
    //                 'Content-Type': 'application/json'
    //             },
    //             body: JSON.stringify({
    //                 "state": state,
    //                 "another": "another"
    //             })
    //         }
    //     ).then(
    //         response => response.json()
    //     )
    //         .then(
    //             data => { console.log("success: ", data); }
    //         );
    //     player.getCurrentState().then(state => {
    //         (!state) ? active = false : active = true;
    //     });

    // }));

    document.getElementById('togglePlayBtn').onclick = function () {
        // TODO: Replace this with a call directly to the play/pause api endpoint, so i can move it out of this embedded nonsense
        function updateButton() {
            var playBtnHtml = `
                <div id="togglePlayPlayIcon">
                    <svg class="h-20 w-20" xmlns="http://www.w3.org/2000/svg" height="48px" viewBox="0 0 24 24" width="48px" fill="#000000"><path d="M0 0h24v24H0V0z" fill="none" />
                                        <path
                                            d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 14.5v-9l6 4.5-6 4.5z" />
                    </svg>
                </div>`;

            var pauseBtnHtml = `
                <div id="togglePlayPauseIcon">
                    <svg class="h-20 w-20" xmlns="http://www.w3.org/2000/svg"
                        enable-background="new 0 0 24 24" height="48px" viewBox="0 0 24 24" width="48px"
                        fill="#000000">
                        <g>
                            <rect fill="none" height="24" width="24" />
                            <rect fill="none" height="24" width="24" />
                            <rect fill="none" height="24" width="24" />
                        </g>
                        <g>
                            <g />
                            <path
                                d="M12,2C6.48,2,2,6.48,2,12s4.48,10,10,10s10-4.48,10-10S17.52,2,12,2z M11,16H9V8h2V16z M15,16h-2V8h2V16z" />
                        </g>
                    </svg>
                </div>`;

            var playBtn = document.querySelector("#togglePlayBtn");

            player.getCurrentState().then(state => {
                if (state.paused) {
                    playBtn.innerHTML = pauseBtnHtml;
                } else {
                    playBtn.innerHTML = playBtnHtml;
                }
            });
            // var button = document.querySelector("#togglePlay");
        }
        player.togglePlay();
        updateButton();
    };

    player.connect();
};