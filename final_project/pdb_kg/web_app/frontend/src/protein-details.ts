import { css, html, LitElement, PropertyValues, TemplateResult } from "lit";
import { property } from "lit/decorators.js";
import {
  AnnotationResponse,
  EntryResponse,
  ProteinResponse,
  Publication,
} from "typescript-axios";
import { getAnnotation, getEntry } from "./api-client";

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
   * Maximum length we allow for annotation names.
   */
  private static MAX_ANNOTATION_NAME_LENGTH = 10;

  /**
   * The info for the protein we want to render.
   */
  @property({ attribute: false })
  protein!: ProteinResponse;

  /**
   * The info for the entry corresponding to this protein.
   */
  @property({ attribute: false })
  private _entry!: EntryResponse;

  /**
   * The annotation info for all the annotations that this protein has.
   * It is okay also if this includes extraneous annotations.
   */
  @property({ attribute: false })
  private _annotations: AnnotationResponse[] = [];

  /**
   * Updates the information about a specific protein from the backend.
   * @private
   */
  private updateProteinInfo() {
    if (!this.protein) {
      // We don't have any protein, so there's nothing to update.
      return;
    }

    // Get information for all the annotations.
    const annotationIds = [...this.protein.annotationUuids];
    const annotationPromises = annotationIds.map((id) => getAnnotation(id));
    Promise.all(annotationPromises).then((annotations) => {
      this._annotations = annotations;
    });

    // Get information for the entry.
    if (this.protein.entryUuid) {
      getEntry(this.protein.entryUuid).then((entry) => {
        this._entry = entry;
      });
    }
  }

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

    // Truncate name if it's too long.
    let annotationName = annotation.name;
    if (annotationName.length > this.MAX_ANNOTATION_NAME_LENGTH) {
      annotationName =
        annotationName.slice(0, this.MAX_ANNOTATION_NAME_LENGTH) + "...";
    }

    return html`
      <div class="chip">
        <a
          class="tooltip-bottom"
          data-tooltip="${annotation.description}"
          href="${ontologyUrl}"
          target="_blank"
          rel="noopener"
        >
          ${annotationName}
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
    for (const annotation of this._annotations) {
      uuidToAnnotation.set(annotation.uuid as string, annotation);
    }

    if (!this.protein) {
      // We have no data yet. Don't show anything.
      return html``;
    }

    return html`
      <link rel="stylesheet" href="static/pdb-kg.css" />

      <div class="card">
        <span class="card-title"
          >${this.protein.entryId}/${this.protein.id}</span
        >
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
                  ${this._entry?.publications.map((publication) =>
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

  /**
   * @inheritDoc
   */
  protected updated(changedProperties: PropertyValues) {
    if (changedProperties.has("protein")) {
      // Update dependent protein data.
      this.updateProteinInfo();
    }
  }
}
