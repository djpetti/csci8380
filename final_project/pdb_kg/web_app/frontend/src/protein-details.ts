import { css, html, LitElement, TemplateResult } from "lit";
import { property } from "lit/decorators.js";
import {
  AnnotationResponse,
  EntryResponse,
  ProteinResponse,
  Publication,
} from "typescript-axios";
import { ANNOTATIONS, ENTRIES, PROTEINS } from "./example_data";

/**
 * Displays detailed information about a protein.
 */
export class ProteinDetails extends LitElement {
  static tagName: string = "protein-details";
  static styles = css`
    .bold {
      font-weight: bold;
    }
  `;

  /**
   * Base URL for gene ontology annotations.
   */
  private static GENE_ONTOLOGY_URL = "http://amigo.geneontology.org/amigo/term";

  /**
   * The info for the protein we want to render.
   */
  @property({ attribute: false })
  protein: ProteinResponse = PROTEINS[0];

  /**
   * The info for the entry corresponding to this protein.
   */
  @property({ attribute: false })
  entry: EntryResponse = ENTRIES[0];

  /**
   * The annotation info for all the annotations that this protein has.
   * It is okay also if this includes extraneous annotations.
   */
  @property({ attribute: false })
  annotations: AnnotationResponse[] = ANNOTATIONS;

  /**
   * Generates a simple abbreviated name for a publication, as you might
   * use in a citation. It is of the form "Petti et al., 2021".
   * @param {Publication} publication The publication to abbreviate.
   * @return {string} The abbreviated name.
   * @private
   */
  private static abbreviatePublication(publication: Publication): string {
    // Create a short identifier for the publication.
    const firstAuthor = publication.authors[0].split(" ");
    const firstAuthorLastName = firstAuthor[firstAuthor.length - 1];

    let authorSuffix = "";
    if (publication.authors.length > 1) {
      // If there is more than one author, add "et al".
      authorSuffix = " et al";
    }

    return `${firstAuthorLastName}${authorSuffix}, ${publication.year}`;
  }

  /**
   * Creates the HTML for representing a specific publication.
   * @param {Publication} publication The publication to render.
   * @return {TemplateResult} The filled HTML template.
   * @private
   */
  private static renderPublication(publication: Publication): TemplateResult {
    const abbreviatedName = ProteinDetails.abbreviatePublication(publication);

    return html`
      <div class="chip">
        <p class="tooltip-bottom" data-tooltip="${publication.title}">
          ${abbreviatedName}
        </p>
      </div>
    `;
  }

  /**
   * Creates the HTML for representing a specific annotation.
   * @param {AnnotationResponse} annotation The annotation to render.
   * @return {TemplateResult} The filled HTML template.
   * @private
   */
  private static renderAnnotation(
    annotation: AnnotationResponse
  ): TemplateResult {
    // Create the URL for the gene ontology description.
    const ontologyUrl = `${ProteinDetails.GENE_ONTOLOGY_URL}/${annotation.id}`;

    return html`
      <div class="chip">
        <a
          class="tooltip-bottom"
          data-tooltip="${annotation.description}"
          href="${ontologyUrl}"
          target="_blank"
          rel="noopener"
        >
          ${annotation.name}
        </a>
      </div>
    `;
  }

  /**
   * @inheritDoc
   */
  protected render() {
    // Map annotations by their UUIDs for easy access.
    const uuidToAnnotation: Map<string, AnnotationResponse> = new Map<
      string,
      AnnotationResponse
    >();
    for (const annotation of this.annotations) {
      uuidToAnnotation.set(annotation.uuid as string, annotation);
    }

    return html`
      <link rel="stylesheet" href="static/pdb-kg.css" />

      <div class="card">
        <span class="card-title">${this.protein.id}</span>
        <div class="card-content">
          <table>
            <tbody>
              <tr>
                <td class="bold">Name</td>
                <td>${this.protein.name}</td>
              </tr>
              <tr>
                <td class="bold">Published By</td>
                <td>
                  ${this.entry.publications.map((publication) =>
                    ProteinDetails.renderPublication(publication)
                  )}
                </td>
              </tr>
              <tr>
                <td class="bold">Annotations</td>
                <td>
                  ${[...this.protein.annotationUuids].map((uuid) =>
                    // Don't render annotations that we don't have details for.
                    uuidToAnnotation.has(uuid)
                      ? ProteinDetails.renderAnnotation(
                          uuidToAnnotation.get(uuid) as AnnotationResponse
                        )
                      : html``
                  )}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    `;
  }
}
