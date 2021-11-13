import { Controller } from "@hotwired/stimulus";

export default class extends Controller {
    // TODO: Handle failure to vote and show the user
    // static targets = ["accessToken"];

    next(event) {
        event.preventDefault();
        const value = event.target.dataset.value;
        console.log(value);
        console.log(event);
        console.log(this.data);
        console.log(event.target.dataset.value);

    }
}