console.log("you made it to party");

function pingSetNowPlaying() {
    var party_id = window.location.pathname.split("/")[2];
    console.log("Pinging server to tell it to update the nowplyaing cuz I skipped to next");
    fetch("http://localhost:5000/set_now_playing/" + party_id)
        .then(
            response => response.text()
        )
        .then(
            data => console.log(data)
        );
}

function transferPlayback() {
    console.log("attempting to transer feedback..");
    fetch(
        'https://api.spotify.com/v1/me/player',
        {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                // 'Authorization': "Bearer " + params.access_token
                'Authorization': "Bearer " + localStorage.tq_oauth_token
            },
            body: JSON.stringify({
                "device_ids": [localStorage.tq_oath_current_device_id]
            })
        }
    ).then(
        response => {
            return response;
        }
    )
        .then(
            data => {
                pingSetNowPlaying();
                console.log("success: ", data);
            }
        );
}

console.log("made it past first func def");

function nextTrack() {
    fetch(
        'https://api.spotify.com/v1/me/player/next',
        {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': "Bearer " + localStorage.tq_oauth_token
            }
        }
    ).then(
        response => {
            console.log(response.status);
            return response.text();
        },
        error => { console.log(error); console.log("i'm in the first error handler..."); }
    )
        .then(
            data => { console.log("success: ", data); pingSetNowPlaying(); },
            error => { console.log(error); console.log("i'm in the second erro rhandled..."); }
        );
}

function prevTrack() {
    fetch(
        'https://api.spotify.com/v1/me/player/previous',
        {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': "Bearer " + localStorage.tq_oauth_token
            }
        }
    ).then(
        response => {
            console.log(response.status);
            return response.text();
        },
        error => { console.log(error); console.log("i'm in the first error handler..."); }
    )
        .then(
            data => { console.log("success: ", data); pingSetNowPlaying(); },
            error => { console.log(error); console.log("i'm in the second erro rhandled..."); }
        );
}


// document.getElementById('transferPlayback').onclick = function () {

// };

function btnEventListeners() {
    window.onload = function () {
        var transferPlaybackBtn = document.querySelector('#transferPlayback');
        var nextBtn = document.querySelector('#nextBtn');
        var prevBtn = document.querySelector('#prevBtn');
        if (transferPlaybackBtn) {
            transferPlaybackBtn.addEventListener("click", transferPlayback);
        }
        else {
            console.log("No 'transferPlayback' button found");
        }

        if (nextBtn) {
            nextBtn.addEventListener("click", nextTrack);
        }
        else {
            console.log("No 'prevBtn' button found");
        }

        if (prevBtn) {
            prevBtn.addEventListener("click", prevTrack);
        }
        else {
            console.log("No 'prevBtn' button found");
        }
    };
    console.log("i'm under where i added event listeners");
}

btnEventListeners();


