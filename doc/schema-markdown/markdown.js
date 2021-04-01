// Licensed under the MIT License
// https://github.com/craigahobbs/chisel/blob/master/LICENSE

import {getBaseURL, isAbsoluteURL} from './util.js';
import {SchemaMarkdownParser} from './parser.js';
import {validateType} from './schema.js';


// The Mardown model defined as Schema Markdown
const markdownModelSmd = `\
# Markdown document struct
struct Markdown

    # The markdown document's parts
    MarkdownPart[len < 1000] parts


# Markdown document part struct
union MarkdownPart

    # A paragraph
    Paragraph paragraph

    # A horizontal rule (value is ignored)
    object(nullable) hr

    # A list
    List list

    # A code block
    CodeBlock codeBlock


# Paragraph markdown part struct
struct Paragraph

    # The paragraph style
    optional ParagraphStyle style

    # The paragraph span array
    Span[len > 0, len < 1000] spans


# Paragraph style enum
enum ParagraphStyle
    h1
    h2
    h3
    h4
    h5
    h6


# Paragraph span struct
union Span

    # Text span
    string(len > 0, len < 1000) text

    # Line break (value is ignored)
    object(nullable) br

    # Style span
    StyleSpan style

    # Link span
    LinkSpan link

    # Image span
    ImageSpan image


# Style span struct
struct StyleSpan

    # The span's character style
    CharacterStyle style

    # The contained spans
    Span[len > 0, len < 1000] spans


# Character style enum
enum CharacterStyle
    bold
    italic


# Link span struct
struct LinkSpan

    # The link's URL
    string(len > 0, len < 1000) href

    # The image's title
    optional string(len > 0, len < 1000) title

    # The contained spans
    Span[len > 0, len < 1000] spans


# Image span struct
struct ImageSpan

    # The image URL
    string(len > 0, len < 1000) src

    # The image's alternate text
    string(len > 0, len < 1000) alt

    # The image's title
    optional string(len > 0, len < 1000) title


# List markdown part struct
struct List

    # The list is numbered and this is starting number
    optional int(>= 0) start

    # The list's items
    ListItem[len > 0, len < 1000] items


# List item struct
struct ListItem

    # The markdown document's parts
    MarkdownPart[len > 0, len < 1000] parts


# Code block markdown part struct
struct CodeBlock

    # The code block's language
    optional string(len > 0, len < 100) language

    # The code block's text lines
    string[len < 1000] lines
`;


// The Markdown model
export const markdownModel = {
    'title': 'The Markdown Model',
    'types': (new SchemaMarkdownParser(markdownModelSmd)).types
};


/**
 * Generate an element model from a markdown model
 *
 * @param {Object} markdown - The markdown model
 * @param {?string} url - The markdown file's URL
 * @param {?Object} codeBlockLanguages - Optional map of language to code block render function with signature (lines) => elements.
 * @returns {Object[]}
 */
export function markdownElements(markdown, url = null, codeBlockLanguages = null) {
    // Parse the markdown
    const validatedMarkdown = validateType(markdownModel.types, 'Markdown', markdown);

    // Generate an element model from the markdown model parts
    return markdownPartElements(validatedMarkdown.parts, url, codeBlockLanguages);
}


// Helper function to generate an element model from a markdown part model array
function markdownPartElements(parts, url, codeBlockLanguages) {
    const partElements = [];
    for (const markdownPart of parts) {
        // Paragraph?
        /* istanbul ignore else */
        if ('paragraph' in markdownPart) {
            const {paragraph} = markdownPart;
            partElements.push({
                'html': 'style' in paragraph ? paragraph.style : 'p',
                'elem': paragraphSpanElements(paragraph.spans, url)
            });

        // Horizontal rule?
        } else if ('hr' in markdownPart) {
            partElements.push({'html': 'hr'});

        // List?
        } else if ('list' in markdownPart) {
            const {list} = markdownPart;
            partElements.push({
                'html': 'start' in list ? 'ol' : 'ul',
                'attr': 'start' in list && list.start > 1 ? {'start': `${list.start}`} : null,
                'elem': list.items.map((item) => ({
                    'html': 'li',
                    'elem': markdownPartElements(item.parts, url, codeBlockLanguages)
                }))
            });

        // Code block?
        } else if ('codeBlock' in markdownPart) {
            const {codeBlock} = markdownPart;

            // Render the code block elements
            if (codeBlockLanguages !== null && 'language' in codeBlock && codeBlock.language in codeBlockLanguages) {
                partElements.push(codeBlockLanguages[codeBlock.language](codeBlock));
            } else {
                partElements.push(
                    {'html': 'pre', 'elem': {'html': 'code', 'elem': codeBlock.lines.map((line) => ({'text': `${line}\n`}))}}
                );
            }
        }
    }

    return partElements;
}


// Helper function to generate an element model from a markdown span model array
function paragraphSpanElements(spans, url) {
    const spanElements = [];
    for (const span of spans) {
        // Text span?
        /* istanbul ignore else */
        if ('text' in span) {
            spanElements.push({'text': span.text});

        // Line break?
        } else if ('br' in span) {
            spanElements.push({'html': 'br'});

        // Style span?
        } else if ('style' in span) {
            const {style} = span;
            spanElements.push({
                'html': style.style === 'italic' ? 'em' : 'strong',
                'elem': paragraphSpanElements(style.spans, url)
            });

        // Link span?
        } else if ('link' in span) {
            const {link} = span;
            const href = url !== null && !isAbsoluteURL(link.href) ? `${getBaseURL(url)}${link.href}` : link.href;
            const linkElements = {
                'html': 'a',
                'attr': {'href': href},
                'elem': paragraphSpanElements(link.spans, url)
            };
            if ('title' in link) {
                linkElements.attr.title = link.title;
            }
            spanElements.push(linkElements);

        // Image span?
        } else if ('image' in span) {
            const {image} = span;
            const src = url !== null && !isAbsoluteURL(image.src) ? `${getBaseURL(url)}${image.src}` : image.src;
            const imageElement = {
                'html': 'img',
                'attr': {'src': src, 'alt': image.alt}
            };
            if ('title' in image) {
                imageElement.attr.title = image.title;
            }
            spanElements.push(imageElement);
        }
    }
    return spanElements;
}


// Markdown regex
const rIndent = /^(?<indent>\s*)(?<notIndent>.*)$/;
const rHeading = /^\s*(?<heading>#{1,6})\s+(?<text>.*?)\s*$/;
const rHeadingAlt = /^\s*(?<heading>=+|-+)\s*$/;
const rHorizontal = /^(?:(?:\s*\*){3,}|(?:\s*-){3,}|(?:\s*_){3,})\s*$/;
const rFenced = /^(?<fence>\s*(?:`{3,}|~{3,}))(?:\s*(?<language>.+?))?\s*$/;
const rList = /^(?<indent>\s*(?<mark>-|\*|\+|[0-9]\.|[1-9][0-9]+\.)\s+)(?<line>.*?)\s*$/;
const rSpans = new RegExp(
    '(?<br>\\s{2}$)|' +
        '(?<link>!?\\[)(?<linkText>[\\s\\S]*?)\\]\\((?<linkHref>[^\\s]+?)(?:\\s*"(?<linkTitle>[\\s\\S]*?)"\\s*)?\\)|' +
        '(?<linkAlt><)(?<linkAltHref>[[a-z]+:[^\\s]*?)>|' +
        '(?<boldItalic>\\*{3})(?!\\s)(?<boldItalicText>[\\s\\S]*?[^\\s]\\**)\\*{3}|' +
        '(?<bold>\\*{2})(?!\\s)(?<boldText>[\\s\\S]*?[^\\s]\\**)\\*{2}|' +
        '(?<italic>\\*)(?!\\s)(?<italicText>[\\s\\S]*?[^\\s]\\**)\\*',
    'mg'
);
const rEscape = /\\(\\|\*|_|\{|\}|\[|\]|\(|\)|#|\+|-|\.|!)/g;


/**
 * Parse markdown text or text lines into a markdown model
 *
 * @param {string|string[]} markdown - Markdown text or text lines
 * @returns {Object} The markdown model
 */
export function markdownParse(markdown) {
    const markdownParts = [];
    const parts = [[0, null, 0]];
    let paragraph = null;
    let paragraphFenced = null;
    let lines = [];

    // Helper function to add a markdown part
    const addPart = (part) => {
        const [, topList] = parts[parts.length - 1];
        if (topList !== null) {
            const {items} = topList.list;
            items[items.length - 1].parts.push(part);
        } else {
            markdownParts.push(part);
        }
    };

    // Helper function to close the current part
    const closeParagraph = (paragraphStyle = null) => {
        // Code block?
        if (paragraph !== null) {
            // Strip trailing blank lines
            let ixLine;
            for (ixLine = lines.length - 1; ixLine >= 0; ixLine--) {
                if (lines[ixLine] !== '') {
                    break;
                }
            }
            paragraph.codeBlock.lines = lines.splice(0, ixLine + 1);
            paragraph = null;
            paragraphFenced = null;
        } else if (lines.length) {
            // Paragraph
            const paragraphPart = {'paragraph': {'spans': paragraphSpans(lines.join('\n'))}};
            if (paragraphStyle !== null) {
                paragraphPart.paragraph.style = paragraphStyle;
            }
            addPart(paragraphPart);
        }
        lines = [];
    };

    // Helper function to get the correct [indent, list, listIndent] tuple for the given indent
    const updateParts = (indent, isList = false) => {
        // Find the part with the lesser or equal indent
        for (let ixPart = parts.length - 1; ixPart > 0; ixPart--) {
            const [curIndent,, curListIndent] = parts[ixPart];
            if (indent >= (isList ? curListIndent : curIndent)) {
                break;
            }
            parts.pop();
        }
        return parts[parts.length - 1];
    };

    // Helper function to add a paragraph line
    const addLine = (line, lineIndent, codeBlockIndent) => {
        if (lines.length) {
            // Code block line? If so, trip the indent
            if (paragraph !== null) {
                lines.push(line.slice(codeBlockIndent));
            } else {
                lines.push(line);
            }
        } else {
            const [curIndent] = updateParts(lineIndent);
            lines.push(line.slice(curIndent));
        }
    };

    // Process markdown text line by line
    for (const markdownString of (typeof markdown === 'string' ? [markdown] : markdown)) {
        for (const line of markdownString.split('\n')) {
            const matchLine = line.match(rIndent);
            const lineIndent = matchLine.groups.indent.length;
            const emptyLine = matchLine.groups.notIndent === '';
            const matchHeading = emptyLine ? null : line.match(rHeading);
            const matchHeadingAlt = emptyLine ? null : line.match(rHeadingAlt);
            const matchFenced = emptyLine ? null : line.match(rFenced);
            const matchList = emptyLine ? null : line.match(rList);
            const [topIndent] = parts[parts.length - 1];
            const codeBlockIndent = topIndent + 4;

            // Empty line?
            if (emptyLine) {
                // Close any open paragraph
                if (paragraph !== null) {
                    addLine(line, lineIndent, topIndent);
                } else {
                    closeParagraph();
                }

            // Code block start?
            } else if (!lines.length && lineIndent >= codeBlockIndent) {
                // Add the code block part
                paragraph = {'codeBlock': {}};
                addPart(paragraph);
                lines.push(line.slice(codeBlockIndent));

            // Fenced code start?
            } else if (paragraphFenced === null && matchFenced !== null && lineIndent < codeBlockIndent) {
                // Close any open paragraph
                closeParagraph();

                // Add the code block part
                paragraph = {'codeBlock': {}};
                if (typeof matchFenced.groups.language !== 'undefined') {
                    paragraph.codeBlock.language = matchFenced.groups.language;
                }
                paragraphFenced = matchFenced.groups.fence;
                addPart(paragraph);

            // Fenced code end?
            } else if (paragraphFenced !== null && matchFenced !== null && paragraphFenced.startsWith(matchFenced.groups.fence) &&
                       typeof matchFenced.groups.language === 'undefined') {
                // Close the code block
                closeParagraph();

            // Fenced code line?
            } else if (paragraphFenced !== null && matchFenced === null) {
                // Add the code line
                addLine(line, lineIndent, topIndent);

            // Heading?
            } else if (matchHeading !== null && lineIndent < codeBlockIndent) {
                // Close any open paragraph
                closeParagraph();

                // Add the heading paragraph markdown part
                updateParts(lineIndent);
                lines = [matchHeading.groups.text];
                closeParagraph(`h${matchHeading.groups.heading.length}`);

            // Heading (alternate syntax)?
            } else if (matchHeadingAlt !== null && lineIndent < codeBlockIndent && parts.length === 1 &&
                       lines.length && paragraph === null) {
                // Add the heading paragraph markdown part
                closeParagraph(matchHeadingAlt.groups.heading.startsWith('=') ? 'h1' : 'h2');

            // Horizontal rule?
            } else if (rHorizontal.test(line) && lineIndent < codeBlockIndent) {
                // Close any open paragraph
                closeParagraph();

                // Add the heading paragraph markdown part
                updateParts(lineIndent);
                addPart({'hr': null});

            // List?
            } else if (matchList !== null && lineIndent < codeBlockIndent) {
                // Close any open paragraph
                closeParagraph();

                // New list?
                const [curIndent, curList] = updateParts(lineIndent, true);
                if (curList === null || lineIndent >= curIndent) {
                    // Add the new list part
                    const list = {'list': {'items': [{'parts': []}]}};
                    const start = parseInt(matchList.groups.mark, 10);
                    if (!isNaN(start)) {
                        list.list.start = start;
                    }
                    addPart(list);
                    parts.push([matchList.groups.indent.length, list, lineIndent]);
                } else {
                    // Push the new list item
                    const listItem = {'parts': []};
                    curList.list.items.push(listItem);
                }

                // Add the text line
                lines.push(matchList.groups.line);

            // Text line
            } else {
                // End code block first?
                if (paragraph !== null && lineIndent < codeBlockIndent) {
                    closeParagraph();
                }

                // Add the paragraph line
                addLine(line, lineIndent, codeBlockIndent);
            }
        }
    }

    // Close any open paragraph
    closeParagraph();

    return {'parts': markdownParts};
}


// Helper function to remove escapes from a string
function removeEscapes(text) {
    return text.replace(rEscape, '$1');
}


// Helper function to translate markdown paragraph text to a markdown paragraph span model array
function paragraphSpans(text) {
    const spans = [];

    // Iterate the span matches
    let ixSearch = 0;
    for (const match of text.matchAll(rSpans)) {
        // Add any preceding text
        if (ixSearch < match.index) {
            spans.push({'text': removeEscapes(text.slice(ixSearch, match.index))});
        }


        // Line break?
        /* istanbul ignore else */
        if (typeof match.groups.br !== 'undefined') {
            spans.push({'br': null});

        // Link span?
        } else if (match.groups.link === '[') {
            const span = {'link': {'href': removeEscapes(match.groups.linkHref), 'spans': paragraphSpans(match.groups.linkText)}};
            if (typeof match.groups.linkTitle !== 'undefined') {
                span.link.title = removeEscapes(match.groups.linkTitle);
            }
            spans.push(span);

        // Link span (alternate syntax)?
        } else if (match.groups.linkAlt === '<') {
            spans.push({'link': {'href': removeEscapes(match.groups.linkAltHref), 'spans': paragraphSpans(match.groups.linkAltHref)}});

        // Image span?
        } else if (match.groups.link === '![') {
            const span = {'image': {'src': removeEscapes(match.groups.linkHref), 'alt': removeEscapes(match.groups.linkText)}};
            if (typeof match.groups.linkTitle !== 'undefined') {
                span.image.title = removeEscapes(match.groups.linkTitle);
            }
            spans.push(span);

        // Bold-italic style-span
        } else if (match.groups.boldItalic === '***') {
            spans.push({'style': {'style': 'bold', 'spans': [
                {'style': {'style': 'italic', 'spans': paragraphSpans(match.groups.boldItalicText)}}
            ]}});

        // Bold style-span
        } else if (match.groups.bold === '**') {
            spans.push({'style': {'style': 'bold', 'spans': paragraphSpans(match.groups.boldText)}});

        // Italic style-span
        } else if (match.groups.italic === '*') {
            spans.push({'style': {'style': 'italic', 'spans': paragraphSpans(match.groups.italicText)}});
        }

        ixSearch = match.index + match[0].length;
    }

    // Add any remaining text
    if (ixSearch < text.length) {
        spans.push({'text': removeEscapes(text.slice(ixSearch))});
    }

    return spans;
}
