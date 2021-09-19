import { css, html, LitElement, property, TemplateResult } from "lit-element";
import { ConflictCheckResult } from "typescript-axios";

/**
 * Element that represents a table with paper information.
 */
export class PaperTable extends LitElement {
  static tagName: string = "paper-table";
  static styles = css`
    .hidden {
      display: none;
    }

    table {
      font-family: "Roboto", sans-serif;
      font-weight: 100;
    }

    div.scrollable {
      width: 100%;
      max-width: 30vw;
      overflow: auto;
    }
  `;

  /**
   * Keeps track of the search results.
   */
  @property({ attribute: false })
  searchResults?: ConflictCheckResult;

  /**
   * Generates the body of the papers table from the current search results.
   * @return {TemplateResult} The generated table body.
   * @private
   */
  private getTableBody(): TemplateResult {
    return html`
      <tbody>
        ${this.searchResults?.papers?.map(
          (paper) => html`
            <tr>
              <td>
                <div class="scrollable">${paper.name}</div>
              </td>
              <td>${paper.year}</td>
            </tr>
          `
        )}
      </tbody>
    `;
  }

  /**
   * @inheritDoc
   */
  protected render() {
    // Don't render the table at all if there are no data.
    const tableDisplayClass =
      (this.searchResults?.papers ?? []).length == 0 ? "hidden" : "";

    return html`
      <link
        type="text/css"
        rel="stylesheet"
        href="node_modules/materialize-css/dist/css/materialize.min.css"
        media="screen,projection"
      />

      <table class="striped ${tableDisplayClass}">
        <thead>
          <tr>
            <th>Paper Name</th>
            <th>Year</th>
          </tr>
        </thead>

        ${this.getTableBody()}
      </table>
    `;
  }
}
