import {css, html, LitElement} from "lit-element";

/**
 * Handles the display of search results.
 */
export class SearchResults extends LitElement {
  static tagName: string = "search-results";
  static styles = css`
    #selection {
      margin-right: 20px;
    }

    .fixed-column {
      height: 75vh;
    }

    #details {
      margin-left: 20px;
    }
  `

  /**
   * @inheritDoc
   */
  protected render() {
    return html`
        <link rel="stylesheet" href="static/pdb-kg.css" />

        <!-- 3-column layout -->
        <div class="mc_row center">
            <!-- Protein selection -->
            <div class="column_width1 fixed-column" id="selection">
                <div class="card">
                    <div class="card-content">
                        <p>Here there be proteins...</p>
                    </div>
                </div>
            </div>

            <!-- Graph visualization -->
            <div class="column_width3 fixed-column" id="visualization">
                <div class="card">
                    <span class="card-title">Related</span>
                    <div class="card-content">
                        <p>Graph of related proteins</p>
                    </div>
                </div>
            </div>

            <!-- Protein details -->
            <div class="column_width1 fixed-column" id="details">
              <div class="card">
                  <span class="card-title">Protein 1</span>
                  <div class="card-content">
                      <p>Detailed info on this protein...</p>
                  </div>
              </div>
              <div class="card">
                <span class="card-title">Protein 2</span>
                <div class="card-content">
                    <p>Detailed info on this protein...</p>
                </div>
              </div>
            </div>
        </div>
    `
  }
}
