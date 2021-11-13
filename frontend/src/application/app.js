// This is the scss entry file
import "../styles/index.scss";
// This code taken from https://stimulus.hotwired.dev/handbook/installing
import { Application } from "@hotwired/stimulus";
import { definitionsFromContext } from "@hotwired/stimulus-webpack-helpers";

const application = Application.start();
const context = require.context("./controllers", true, /\.js$/);
application.load(definitionsFromContext(context));
