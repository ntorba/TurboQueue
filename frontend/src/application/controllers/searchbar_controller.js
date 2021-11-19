import { Controller } from "@hotwired/stimulus";

export default class extends Controller {
    // TODO: Handle failure to vote and show the user
    static targets = ["id"];

    search() {
        console.log("here is the closest form thing...");
        console.log(this.element);
        console.log(this.element.closest("form"));
        // this.element.closest("form").requestSubmit();
    }
}