import { LitElement, html, css, property } from "lit-element";
import "@material/mwc-textfield";
import "@material/mwc-button";

/**
 * Main element that handles searching and the display of results.
 */
export class SearchWidget extends LitElement {
  static tagName: string = "search-widget";
  static styles = css`
    .half-screen {
      min-width: 300px;
      max-width: 50%;
    }

    .full-width {
      width: 100%;
    }

    #overview_text {
      color: var(--theme-gray);
      font-family: "Roboto", sans-serif;
      font-weight: 100;
      margin: auto;
      width: 50%;
      text-align: center;
      font-size: x-large;
    }
  `;

  /**
   * The name of the first researcher to check.
   */
  @property({ type: String })
  firstName: string = "";

  /**
   * The name of the second researcher to check.
   */
  @property({ type: String })
  secondName: string = "";

  /**
   * @inheritDoc
   */
  protected render() {
    return html`
      <link rel="stylesheet" href="static/project1.css" />
      <link
        type="text/css"
        rel="stylesheet"
        href="node_modules/materialize-css/dist/css/materialize.min.css"
        media="screen,projection"
      />

      <!-- Search boxes -->
      <div class="row center">
        <div class="column_width1 half-screen">
          <mwc-textfield
            label="Researcher #1 Name"
            id="first_name"
            class="full-width"
            helper="The name of the first researcher"
            value="${this.firstName}"
            @change="${(event: InputEvent) =>
              (this.firstName = (event.target as HTMLInputElement).value)}"
          ></mwc-textfield>
        </div>
        <div class="column_width1 half-screen">
          <mwc-textfield
            label="Researcher #2 Name"
            id="second_name"
            class="full-width"
            helper="The name of the second researcher"
            value="${this.secondName}"
            @change="${(event: InputEvent) =>
              (this.secondName = (event.target as HTMLInputElement).value)}"
          ></mwc-textfield>
        </div>
      </div>

      <!-- Search button -->
      <div class="row center">
        <div class="column_width1">
          <mwc-button label="Search" icon="search"> </mwc-button>
        </div>
      </div>

      <!-- Result overview -->
      <div class="row center">
        <div class="column_width1">
          <h1 id="overview_text">Possible Conflicts Found</h1>
        </div>
      </div>

      <!-- Result table -->
      <div class="row center">
        <div class="column_width1">
          <table class="striped">
            <thead>
              <tr>
                <th>Paper Name</th>
                <th>Year</th>
                <th># of Citations</th>
              </tr>
            </thead>

            <tbody>
              <tr>
                <td>We Put a Camera Somewhere New</td>
                <td>2019</td>
                <td>150</td>
              </tr>
              <tr>
                <td>Hey, I Found a Trove of Old Records!</td>
                <td>2021</td>
                <td>35</td>
              </tr>
              <tr>
                <td>My Colleague is Wrong and I can Finally Prove It</td>
                <td>2018</td>
                <td>1032</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    `;
  }
}
