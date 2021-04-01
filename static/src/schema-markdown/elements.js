// Licensed under the MIT License
// https://github.com/craigahobbs/chisel/blob/master/LICENSE

import {SchemaMarkdownParser} from './parser.js';
import {validateType} from './schema.js';


// The element model defined as Schema Markdown
const elementModelSmd = `\
# An HTML element
struct Element

    # HTML element tag
    optional string(len > 0) html

    # SVG element tag
    optional string(len > 0) svg

    # Text element's text
    optional string text

    # The element's attribute dictionary
    optional Attrs(nullable) attr

    # An element model or an array of element models
    optional object(nullable) elem

    # The element creation callback function
    optional object callback

# An HTML element's attributes collection
typedef string(len > 0) : object(nullable){} Attrs
`;


// The element model
export const elementModel = {
    'title': 'The Element Model',
    'types': (new SchemaMarkdownParser(elementModelSmd)).types
};


/**
 * Validate an element model
 *
 * @param {?(Object|Array)} elements - The element model.
 *     An element model is either null, an element object, or an array of any of these.
 * @throws {Error} Validation error string
 */
export function validateElements(elements) {
    // Array?
    if (Array.isArray(elements)) {
        // Validate the sub-elements
        for (const subElements of elements) {
            validateElements(subElements);
        }

    // Non-null?
    } else if (elements !== null) {
        // Validation error exception helper function
        const throwValueError = (message, value) => {
            const valueStr = `${JSON.stringify(value)}`;
            throw new Error(`${message} ${valueStr.slice(0, 100)} (type '${typeof value}')`);
        };

        // Non-object?
        if (typeof elements !== 'object') {
            throwValueError('Invalid element', elements);
        }

        // Validate the element model
        validateType(elementModel.types, 'Element', elements);

        // Validate creation callback
        if ('callback' in elements && typeof elements.callback !== 'function') {
            throwValueError('Invalid element callback function', elements.callback);
        }

        // Text?
        if ('text' in elements) {
            // Text elements don't have attributes or children
            if ('attr' in elements) {
                throwValueError('Invalid text element member "attr"', elements.text);
            }
            if ('elem' in elements) {
                throwValueError('Invalid text element member "elem"', elements.text);
            }

        // HTML or SVG?
        } else if ('html' in elements || 'svg' in elements) {
            // Validate the sub-elements
            if ('elem' in elements) {
                validateElements(elements.elem);
            }
        } else {
            throwValueError('Missing element key', elements);
        }
    }
}


/**
 * Render an element model
 *
 * @param {Element} parent - The parent element to render within
 * @param {?(Object|Array)} [elements=null] - The element model.
 *     An element model is either null, an element object, or an array of any of these.
 * @param {boolean} [clear=true] - If true, empty parent before rendering
 */
export function renderElements(parent, elements = null, clear = true) {
    validateElements(elements);
    if (clear) {
        parent.innerHTML = '';
    }
    renderElementsHelper(parent, elements);
}


// Helper function to create an Element object and append it to the given parent Element object
function renderElementsHelper(parent, elements) {
    if (Array.isArray(elements)) {
        for (const element of elements) {
            renderElementsHelper(parent, element);
        }
    } else if (elements !== null) {
        const element = elements;
        let browserElement;

        // Create an element of the appropriate type
        if ('text' in element) {
            browserElement = document.createTextNode(element.text);
        } else if ('svg' in element) {
            browserElement = document.createElementNS('http://www.w3.org/2000/svg', element.svg);
        } else {
            browserElement = document.createElement(element.html);
        }

        // Add attributes, if any, to the newly created element
        if ('attr' in element && element.attr !== null) {
            for (const [attr, value] of Object.entries(element.attr)) {
                // Skip null values
                if (value !== null) {
                    browserElement.setAttribute(attr, `${value}`);
                }
            }
        }

        // Create the newly created element's child elements
        if ('elem' in element) {
            renderElementsHelper(browserElement, element.elem);
        }

        // Add the child element
        parent.appendChild(browserElement);

        // Call the element callback, if any
        if ('callback' in element) {
            element.callback(browserElement);
        }
    }
}
