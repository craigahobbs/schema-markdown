// Licensed under the MIT License
// https://github.com/craigahobbs/schema-markdown/blob/master/LICENSE


/** The non-breaking space character. */
export const nbsp = String.fromCharCode(160);


/**
 * Check if a URL is absolute
 *
 * @param {string} url - The URL
 * @returns {bool} true if the URL is absolute, false otherwise
 */
export function isAbsoluteURL(url) {
    return rAbsoluteURL.test(url);
}

const rAbsoluteURL = /^[a-z]{3,5}:/;


/**
 * Get a URL's base URL
 *
 * @param {string} url - The URL
 * @returns {string} The base URL or the URL
 */
export function getBaseURL(url) {
    const ixBaseSlash = url.lastIndexOf('/');
    return ixBaseSlash === -1 ? '' : url.slice(0, ixBaseSlash + 1);
}


/**
 * Create a resource location string for the local server.
 *
 * @param {Object} [hash=null] - The hash parameters
 * @param {Object} [queyr=null] - The query string parameters
 * @param {string} [pathname=null] - The location's path. If null, use "window.location.pathname".
 * @returns {string}
 */
export function href(hash = null, query = null, pathname = null) {
    // Encode the hash parameters, if any
    let hashStr = '';
    if (hash !== null) {
        hashStr = `#${encodeParams(hash)}`;
    } else if (query === null) {
        hashStr = '#';
    }

    // Encode the query parameters, if any
    let queryStr = '';
    if (query !== null) {
        queryStr = `?${encodeParams(query)}`;
        if (queryStr === '?') {
            queryStr = '';
        }
    }

    // No pathname provided? If so, provide a default.
    let pathname_ = pathname;
    if (pathname_ === null) {
        pathname_ = window.location.pathname;
    }

    return `${pathname_}${queryStr}${hashStr}`;
}


/**
 * Encode an object as a query/hash string. Dictionaries, lists, and tuples are recursed. Each member key is expressed
 * in fully-qualified form. List keys are the index into the list, and are in order.
 *
 * @param {Object} obj - The parameters object
 * @returns {string}
 */
export function encodeParams(obj) {
    return encodeParamsHelper(obj).join('&');
}


// Helper function for encodeParams
function encodeParamsHelper(obj, memberFqn = null, keyValues = []) {
    const objType = typeof obj;
    if (Array.isArray(obj)) {
        if (obj.length === 0) {
            keyValues.push(memberFqn !== null ? `${memberFqn}=` : '');
        } else {
            for (let ix = 0; ix < obj.length; ix++) {
                encodeParamsHelper(obj[ix], memberFqn !== null ? `${memberFqn}.${ix}` : `${ix}`, keyValues);
            }
        }
    } else if (obj instanceof Date) {
        const objEncoded = encodeURIComponent(obj.toISOString());
        keyValues.push(memberFqn !== null ? `${memberFqn}=${objEncoded}` : `${objEncoded}`);
    } else if (obj !== null && typeof obj === 'object') {
        const keys = Object.keys(obj).sort();
        if (keys.length === 0) {
            keyValues.push(memberFqn !== null ? `${memberFqn}=` : '');
        } else {
            for (const key of keys) {
                const keyEncoded = encodeParamsHelper(key);
                encodeParamsHelper(obj[key], memberFqn !== null ? `${memberFqn}.${keyEncoded}` : `${keyEncoded}`, keyValues);
            }
        }
    } else if (obj === null || objType === 'boolean' || objType === 'number') {
        keyValues.push(memberFqn !== null ? `${memberFqn}=${obj}` : `${obj}`);
    } else {
        const objEncoded = encodeURIComponent(obj);
        keyValues.push(memberFqn !== null ? `${memberFqn}=${objEncoded}` : `${objEncoded}`);
    }
    return keyValues;
}


/**
 * Decode an object from a query/hash string. Each member key of the query string is expressed in fully-qualified
 * form. List keys are the index into the list, must be in order.
 *
 * @param {string} [paramStr=null] - The parameters string.
 *     If null, "window.location.hash.substring(1)" is used.
 * @returns {Object}
 */
export function decodeParams(paramStr = null) {
    // No parameters string provided? If so, provide a default
    let paramStr_ = paramStr;
    if (paramStr_ === null) {
        paramStr_ = window.location.hash.substring(1);
    }

    // Decode the parameter string key/values
    const result = [null];
    paramStr_.split('&').filter((keyValue) => keyValue.length).forEach(
        (keyValue, ixKeyValue, keyValuesFiltered) => {
            const [keyFqn, valueEncoded = null] = keyValue.split('=');
            if (valueEncoded === null) {
                // Ignore anchor tags
                if (ixKeyValue === keyValuesFiltered.length - 1) {
                    return;
                }
                throw new Error(`Invalid key/value pair '${keyValue.slice(0, 100)}'`);
            }
            const value = decodeURIComponent(valueEncoded);

            // Find/create the object on which to set the value
            let parent = result;
            let keyParent = 0;
            const keys = keyFqn.split('.');
            for (const keyEncoded of keys) {
                let key = decodeURIComponent(keyEncoded);
                let obj = parent[keyParent];

                // Array key?  First "key" of an array must start with "0".
                if (Array.isArray(obj) || (obj === null && key === '0')) {
                    // Create this key's container, if necessary
                    if (obj === null) {
                        obj = [];
                        parent[keyParent] = obj;
                    }

                    // Parse the key as an integer
                    if (isNaN(key)) {
                        throw new Error(`Invalid array index '${key.slice(0, 100)}' in key '${keyFqn.slice(0, 100)}'`);
                    }
                    const keyOrig = key;
                    key = parseInt(key, 10);

                    // Append the value placeholder null
                    if (key === obj.length) {
                        obj.push(null);
                    } else if (key < 0 || key > obj.length) {
                        throw new Error(`Invalid array index '${keyOrig.slice(0, 100)}' in key '${keyFqn.slice(0, 100)}'`);
                    }
                } else {
                    // Create this key's container, if necessary
                    if (obj === null) {
                        obj = {};
                        parent[keyParent] = obj;
                    }

                    // Create the index for this key
                    if (!(key in obj)) {
                        obj[key] = null;
                    }
                }

                // Update the parent object and key
                parent = obj;
                keyParent = key;
            }

            // Set the value
            if (parent[keyParent] !== null) {
                throw new Error(`Duplicate key '${keyFqn.slice(0, 100)}'`);
            }
            parent[keyParent] = value;
        }
    );

    return result[0] !== null ? result[0] : {};
}
