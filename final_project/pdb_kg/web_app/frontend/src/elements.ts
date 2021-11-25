import { LitElement } from "lit";
import { SearchWidget } from "./search-widget";
import { SearchResults } from "./search-results";
import { GraphVisualization } from "./graph-visualization";
import { ProteinSelector } from "./protein-selector";

type LitElementType = typeof LitElement;

interface ComponentType extends LitElementType {
  /** Name of the element tag. */
  tagName: string;
}

/** List of all custom elements. */
const componentClasses: ComponentType[] = [
  SearchWidget,
  SearchResults,
  GraphVisualization,
  ProteinSelector,
];

/**
 * Registers all known web components as custom elements.
 */
export function registerComponents() {
  for (const component of componentClasses) {
    customElements.define(component.tagName, component);
  }
}
