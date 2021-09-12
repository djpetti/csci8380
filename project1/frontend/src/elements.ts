import { LitElement } from "lit-element";
import { SearchWidget } from "./search-widget";
import { PaperTable } from "./paper-table";

type LitElementType = typeof LitElement;

interface ComponentType extends LitElementType {
  /** Name of the element tag. */
  tagName: string;
}

/** List of all custom elements. */
const componentClasses: ComponentType[] = [SearchWidget, PaperTable];

/**
 * Registers all known web components as custom elements.
 */
export function registerComponents() {
  for (const component of componentClasses) {
    customElements.define(component.tagName, component);
  }
}
