import { LitElement } from "lit-element";
type LitElementType = typeof LitElement;
interface ComponentType extends LitElementType {
  /** Name of the element tag. */
  tagName: string;
}

/** List of all custom elements. */
const componentClasses: ComponentType[] = [];

/**
 * Registers all known web components as custom elements.
 */
export function registerComponents() {
  for (const component of componentClasses) {
    customElements.define(component.tagName, component);
  }
}
