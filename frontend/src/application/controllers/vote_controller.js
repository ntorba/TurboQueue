import { Controller } from "@hotwired/stimulus";

export default class extends Controller {
    // TODO: Handle failure to vote and show the user
    static targets = ["vote"];

    vote(event) {
        let postData = async () => {
            try {
                await fetch(
                    'http://localhost:5000/vote',
                    {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            "uri": event.target.id,
                            "another": "another"
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