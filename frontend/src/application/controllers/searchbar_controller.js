import { Controller } from "@hotwired/stimulus";

const party_id = window.location.pathname.split("/")[2];

export default class extends Controller {
    // TODO: Handle failure to vote and show the user
    static targets = ["content", "submit"];

    connect() {
        console.log("CONNECTING SEARCHBAR CONTROLLER....");
    }

    search() {
        console.log(this.element);
        var searchResultsSection = document.querySelector("#searchResultsSection");
        if (this.contentTarget.value.length < 1) {
            searchResultsSection.innerHTML = '';
        }
        else {
            console.log("trying to log content: ");
            console.log(this.contentTarget);
            console.log(this.contentTarget.value);
            console.log(this.submitTarget);
            this.submitTarget.click();
        }
        // console.log("here is the closest form thing...");
        // console.log(this.element);
        // console.log(this.element.closest("form"));
        // this.element.closest("form").requestSubmit();
    }

    clearResults() {
        // var searchResultsSection = document.querySelector("#searchResultsSection");
        // event.preventDefault();
        console.log("got rid of clearing for now");
        // searchResultsSection.innerHTML = '';
    }

    addTrack() {
        console.log("I'm in addTrack baby what's good");
        console.log(this.element);
        console.log(this.element.dataset);
        this.element.dataset.party_id = party_id;
        addSong(this.element.dataset);
        var searchResultsSection = document.querySelector("#searchResultsSection");
        searchResultsSection.innerHTML = '';
    }
}

const addSong = async (track_info) => {
    fetch(
        window.origin + '/add_track',
        {

            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                "track": track_info,
            })
        }
    ).then(
        res => res.json()
    );
};