// Allow use of MWC elements.
import "@material/mwc-top-app-bar-fixed";
import "@material/mwc-textfield";
import "@material/mwc-button";
import "@material/mwc-linear-progress";
import { registerComponents } from "./elements";
import "../css/project1.scss";

window.onload = function () {
  registerComponents();
};
