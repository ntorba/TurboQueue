import { Controller } from "@hotwired/stimulus";

export default class extends Controller {
    // TODO: Handle failure to vote and show the user
    static targets = ["vote"];

    vote(event) {
        var party_id = window.location.pathname.split("/")[2];
        let postData = async () => {
            try {
                await fetch(
                    window.origin + '/vote',
                    {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            "uri": event.target.id,
                            "party_id": party_id
                        })
                    }
                ).then(
                    response => response.json()
                )
                    .then(
                        data => { console.log("success: ", data); }
                    );
            } catch (err) {
                console.log("caught error");
                console.error(`Error: ${err}`);
            }
        };
        postData();
    }
}