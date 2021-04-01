// Licensed under the MIT License
// https://github.com/craigahobbs/chisel/blob/master/LICENSE

import {decodeParams, href} from './schema-markdown/util.js';
import {validateType, validateTypeModel} from './schema-markdown/schema.js';
import {SchemaMarkdownParser} from './schema-markdown/parser.js';
import {UserTypeElements} from './schema-markdown/doc.js';
import {renderElements} from './schema-markdown/elements.js';
import {typeModel as smdTypeModel} from './schema-markdown/typeModel.js';


/**
 * The Chisel documentation application hash parameters type model specification
 */
const docPageTypes = (new SchemaMarkdownParser(`\
# The Schema Markdown documentation application hash parameters struct
struct DocParams

    # Request name to render documentation. If not provided, the request index is displayed.
    optional string(len > 0) name

    # The JSON type model resource URL
    optional string(len > 0) url
`).types);


/**
 * The Chisel documentation application
 *
 * @property {?string} defaultTypeModel - The default type model object
 * @property {?string} defaultTypeModelURL - The default JSON type model resource URL
 * @property {Array} windowHashChangeArgs - The arguments for the window.addEventListener for "hashchange"
 * @property {Object} params - The validated hash parameters object
 */
export class DocPage {
    /**
     * Create a documentation application instance
     *
     * @param {?string|Object} [typeModel=null] - Optional type model (object or resource URL)
     */
    constructor(typeModel = null) {
        if (typeof typeModel === 'string') {
            this.defaultTypeModelURL = typeModel;
            this.defaultTypeModel = null;
        } else {
            this.defaultTypeModel = typeModel !== null ? typeModel : smdTypeModel;
            this.defaultTypeModelURL = null;
        }
        this.windowHashChangeArgs = null;
        this.params = null;
    }

    /**
     * Run the application
     *
     * @param {?string|Object} [typeModel=null] - Optional type model object or JSON type model resource URL
     * @returns {DocPage}
     */
    static run(typeModel = null) {
        const docPage = new DocPage(typeModel);
        docPage.init();
        docPage.render();
        return docPage;
    }

    /**
     * Initialize the global application state
     */
    init() {
        this.windowHashChangeArgs = ['hashchange', () => this.render(), false];
        window.addEventListener(...this.windowHashChangeArgs);
    }

    /**
     * Uninitialize the global application state
     */
    uninit() {
        if (this.windowHashChangeArgs !== null) {
            window.removeEventListener(...this.windowHashChangeArgs);
            this.windowHashChangeArgs = null;
        }
    }

    /**
     * Helper function to parse and validate the hash parameters
     *
     * @param {?string} params - The (hash) params string
     */
    updateParams(params = null) {
        // Clear, then validate the hash parameters (may throw)
        this.params = null;
        this.params = validateType(docPageTypes, 'DocParams', decodeParams(params));
    }

    /**
     * Render the documentation application page
     */
    render() {
        // Validate hash parameters
        try {
            const paramsPrev = this.params;
            this.updateParams();

            // Skip the render if the page params haven't changed
            if (paramsPrev !== null && JSON.stringify(paramsPrev) === JSON.stringify(this.params)) {
                return;
            }
        } catch ({message}) {
            DocPage.renderErrorPage(message);
            return;
        }

        // Clear the page
        renderElements(document.body);

        // Type model URL provided?
        const typeModelURL = 'url' in this.params ? this.params.url : this.defaultTypeModelURL;
        if (typeModelURL !== null) {
            // Load the type model URL
            window.fetch(typeModelURL).
                then((response) => {
                    if (!response.ok) {
                        throw new Error(`Could not fetch type mode '${typeModelURL}': ${response.statusText}`);
                    }
                    return response.json();
                }).
                then((typeModel) => {
                    this.renderTypeModelPage(validateTypeModel(typeModel));
                }).catch(({message}) => {
                    DocPage.renderErrorPage(message);
                });
        } else {
            this.renderTypeModelPage(this.defaultTypeModel);
        }
    }

    /**
     * Helper function to render a type model experience
     *
     * @param {Object} typeModel - A type model
     */
    renderTypeModelPage(typeModel) {
        // Type page?
        if ('name' in this.params) {
            // Unknown type?
            if (!(this.params.name in typeModel.types)) {
                DocPage.renderErrorPage(`Unknown type name '${this.params.name}'`);
            } else {
                this.renderTypePage(typeModel, this.params.name);
            }
            return;
        }

        // Render the index page
        this.renderIndexPage(typeModel);
    }

    /**
     * Helper function to render an index page
     *
     * @param {Object} typeModel - A type model
     */
    renderIndexPage(typeModel) {
        document.title = typeModel.title;
        renderElements(document.body, this.indexPage(typeModel));
    }

    /**
     * Helper function to render a type page
     *
     * @param {Object} typeModel - A type model
     */
    renderTypePage(typeModel, typeName) {
        document.title = typeName;
        renderElements(document.body, this.typePage(typeModel, typeName));
    }

    /**
     * Helper function to render an error page
     */
    static renderErrorPage(message) {
        document.title = 'Error';
        renderElements(document.body, DocPage.errorPage(message));
    }

    /**
     * Helper function to generate the error page's element hierarchy model
     *
     * @param {string} message - The error message
     * @return {Object}
     */
    static errorPage(message) {
        return {
            'html': 'p',
            'elem': {'text': `Error: ${message}`}
        };
    }

    /**
     * Helper function to generate the index page's element hierarchy model
     *
     * @param {Object} typeModel - A type model
     * @returns {Array}
     */
    indexPage(typeModel) {
        // Build the index groups
        const groups = {};
        for (const [userTypeName, userType] of Object.entries(typeModel.types).sort()) {
            let docGroup;
            if ('enum' in userType) {
                docGroup = 'docGroup' in userType.enum ? userType.enum.docGroup : 'Enumerations';
            } else if ('struct' in userType) {
                docGroup = 'docGroup' in userType.struct ? userType.struct.docGroup : 'Structs';
            } else if ('typedef' in userType) {
                docGroup = 'docGroup' in userType.typedef ? userType.typedef.docGroup : 'Typedefs';
            } else {
                docGroup = 'docGroup' in userType.action ? userType.action.docGroup : 'Actions';
            }
            if (!(docGroup in groups)) {
                groups[docGroup] = [];
            }
            groups[docGroup].push(userTypeName);
        }

        // Return the index element model
        return [
            // Title
            {'html': 'h1', 'elem': {'text': typeModel.title}},

            // Groups
            Object.keys(groups).sort().map((group) => [
                {'html': 'h2', 'elem': {'text': group}},
                {
                    'html': 'ul',
                    'attr': {'class': 'chisel-index-list'},
                    'elem': {'html': 'li', 'elem': {'html': 'ul', 'elem': groups[group].sort().map(
                        (name) => ({
                            'html': 'li',
                            'elem': {'html': 'a', 'attr': {'href': href({...this.params, 'name': name})}, 'elem': {'text': name}}
                        })
                    )}}
                }
            ])
        ];
    }

    /**
     * Helper function to generate the request page's element hierarchy model
     *
     * @param {Object} typeModel - A type model
     * @returns {Array}
     */
    typePage(typeModel, typeName) {
        const indexParams = {...this.params};
        delete indexParams.name;
        return [
            // Navigation bar
            {
                'html': 'p',
                'elem': {
                    'html': 'a',
                    'attr': {'href': href(indexParams)},
                    'elem': {'text': 'Back to documentation index'}
                }
            },

            // The user type elements
            (new UserTypeElements(this.params)).getElements(typeModel.types, typeName)
        ];
    }
}
