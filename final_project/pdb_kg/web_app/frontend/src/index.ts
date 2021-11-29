// Allow use of MWC elements.
import "@material/mwc-top-app-bar-fixed";
import "@material/mwc-textfield";
import "@material/mwc-button";
import "@material/mwc-linear-progress";
import "@material/mwc-list";
import { registerComponents } from "./elements";
import "../css/pdb-kg.scss";
import "materialize-css/dist/js/materialize";

window.onload = function () {
  registerComponents();
};
