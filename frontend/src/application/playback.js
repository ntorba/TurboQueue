function pingSetNowPlaying() {
    var party_id = window.location.pathname.split("/")[2];
    console.log("Pinging server to tell it to update the nowplyaing cuz I skipped to next");
    fetch(
        window.origin + "/set_now_playing/" + party_id,
        {
            method: 'PUT',
        }

    )
        .then(
            response => response.text()
        )
        .then(
            data => console.log(data)
        );
}

export function transferPlayback() {
    console.log("attempting to transer feedback..");
    console.log("here is the device id: " + localStorage.tq_oath_current_device_id);
    console.log("here is oauth token: " + localStorage.tq_oauth_token);
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


function nextTrack() {
    var party_id = window.location.pathname.split("/")[2];
    fetch(
        window.origin + "/next_track",
        // 'https://api.spotify.com/v1/me/player/next',
        {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': "Bearer " + localStorage.tq_oauth_token
            },
            body: JSON.stringify({
                "party_id": party_id
            })
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

function addClickListener(id, func) {
    var el = document.querySelector('#' + id);
    if (el) {
        el.addEventListener("click", func);
    }
    else {
        console.log("No element found with id " + id);
    }
}

function btnEventListeners() {
    window.onload = function () {
        // addClickListener("transferPlayback", transferPlayback); I'm doing this automatically now
        addClickListener("nextBtn", nextTrack);
        addClickListener("prevBtn", prevTrack);
    };
    console.log("i'm under where i added event listeners");
}

btnEventListeners();


