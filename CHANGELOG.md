# Changelog

## 1.3.3 (2026-08-06)

- [e1a9c0d](https://github.com/craigahobbs/schema-markdown/commit/e1a9c0d) - migrate package metadata from setup.cfg to pyproject.toml

## 1.3.2 (2026-07-29)

- [651edae](https://github.com/craigahobbs/schema-markdown/commit/651edae) - restructure the parse loop and type validation to align with the bare-script ports

- [f25660c](https://github.com/craigahobbs/schema-markdown/commit/f25660c) - detect circular typedefs in type model validation

- [9dd975c](https://github.com/craigahobbs/schema-markdown/commit/9dd975c) - error on invalid Schema Markdown text input

- [e72ef29](https://github.com/craigahobbs/schema-markdown/commit/e72ef29) - accept scientific-notation int strings

- [a75220b](https://github.com/craigahobbs/schema-markdown/commit/a75220b) - error on sub-keying a scalar value in decode_query_string

## 1.3.1 (2026-07-14)

- [da519b2](https://github.com/craigahobbs/schema-markdown/commit/da519b2) - performance optimizations: 24% faster validation, 14% faster parsing, 100% test coverage

## 1.3.0 (2026-07-13)

- [5a9713c](https://github.com/craigahobbs/schema-markdown/commit/5a9713c)

  **Breaking changes:**

  - validated `uuid` values are now strings (previously converted to `uuid.UUID`)
  - rename `ValidationError.member` to `member_fqn`
  - `date` accepts only date-only strings; `datetime` requires a timezone
  - reject non-canonical `uuid` strings and invalid calendar dates (e.g. February 30)
  - report a syntax error for trailing text after an `action` definition
  - remove Python 3.10 support

  **Other changes:**

  - reformat validation error messages (double-quoted names, JSON-formatted values)
  - improve unit tests

## 1.2.13 (2026-04-25)

- [f6ee10b](https://github.com/craigahobbs/schema-markdown/commit/f6ee10b) - update self-hosting schema docs instructions

## 1.2.12 (2025-11-21)

- [c9f6e29](https://github.com/craigahobbs/schema-markdown/commit/c9f6e29) - update schema documentation instructions

## 1.2.11 (2025-05-09)

- [71ba9b1](https://github.com/craigahobbs/schema-markdown/commit/71ba9b1) - add Python 3.14

- [9e55874](https://github.com/craigahobbs/schema-markdown/commit/9e55874) - remove setup.cfg license classifier

## 1.2.10 (2024-11-08)

- [83a98cb](https://github.com/craigahobbs/schema-markdown/commit/83a98cb) - fix doc typo

## 1.2.9 (2024-11-08)

- [255dda3](https://github.com/craigahobbs/schema-markdown/commit/255dda3) - add `any` builtin type and deprecate `object` builtin type

## 1.2.8 (2024-10-02)

- [a0e8572](https://github.com/craigahobbs/schema-markdown/commit/a0e8572) - add Python 3.13, remove Python 3.8 \(end-of-life\)

## 1.2.7 (2024-04-03)

- [26d8924](https://github.com/craigahobbs/schema-markdown/commit/26d8924) - convert docs to markdown

## 1.2.6 (2023-06-28)

- [195e65c](https://github.com/craigahobbs/schema-markdown/commit/195e65c) - schema-markdown 1.2.6

## 1.2.5 (2023-06-28)

- [d51bdc6](https://github.com/craigahobbs/schema-markdown/commit/d51bdc6) - sync version with pypi

## 1.2.4 (2023-06-28)

- [a71ac70](https://github.com/craigahobbs/schema-markdown/commit/a71ac70) - add python 3.12 support, remove python 3.7 support \(end-of-life\)

## 1.2.3 (2023-05-23)

- [e43aa15](https://github.com/craigahobbs/schema-markdown/commit/e43aa15) - tweak error message, improve unit tests

## 1.2.2 (2022-10-31)

- [f7f0bfe](https://github.com/craigahobbs/schema-markdown/commit/f7f0bfe) - add pyproject.toml and setup.cfg, remove setup.py

## 1.2.1 (2022-08-23)

- [fe59a59](https://github.com/craigahobbs/schema-markdown/commit/fe59a59) - update docs

## 1.2.0 (2022-08-23)

- [e5d8e65](https://github.com/craigahobbs/schema-markdown/commit/e5d8e65) - refactor SchemaMarkdownParser class as parse_schema_markdown function

## 1.1.12 (2022-05-10)

- [8c702f4](https://github.com/craigahobbs/schema-markdown/commit/8c702f4) - remove TypeModel

- [43be8fe](https://github.com/craigahobbs/schema-markdown/commit/43be8fe) - add python 3.11 support

## 1.1.11 (2021-12-11)

- [633e57c](https://github.com/craigahobbs/schema-markdown/commit/633e57c) - allow arbitrary quoted enum values

## 1.1.10 (2021-12-08)

- [26ebc99](https://github.com/craigahobbs/schema-markdown/commit/26ebc99) - fix nullable member issue

## 1.1.9 (2021-11-30)

- [70057af](https://github.com/craigahobbs/schema-markdown/commit/70057af) - fix decode_query_string empty string case

## 1.1.8 (2021-11-30)

- [6370bf5](https://github.com/craigahobbs/schema-markdown/commit/6370bf5) - decode_query_string improvements

## 1.1.7 (2021-10-25)

- [752e0d1](https://github.com/craigahobbs/schema-markdown/commit/752e0d1) - improve compile tool's error output

## 1.1.6 (2021-09-21)

- [57323d9](https://github.com/craigahobbs/schema-markdown/commit/57323d9) - add compile tool referenced types argument

- [4d32558](https://github.com/craigahobbs/schema-markdown/commit/4d32558) - fixes for pylint 2.10

## 1.1.5 (2021-08-24)

- [a3de343](https://github.com/craigahobbs/schema-markdown/commit/a3de343) - update readme

## 1.1.4 (2021-08-18)

- [16a0722](https://github.com/craigahobbs/schema-markdown/commit/16a0722) - updates from python-package-template

## 1.1.3 (2021-08-18)

- [9ae3972](https://github.com/craigahobbs/schema-markdown/commit/9ae3972) - updates from python-package-template

## 1.1.2 (2021-08-12)

- [5f7f3ea](https://github.com/craigahobbs/schema-markdown/commit/5f7f3ea) - updates from python-package-template

## 1.1.1 (2021-07-26)

- [cf2c8d7](https://github.com/craigahobbs/schema-markdown/commit/cf2c8d7) - simplify setup.py

## 1.1.0 (2021-07-22)

- [1badbd4](https://github.com/craigahobbs/schema-markdown/commit/1badbd4) - rename \_\_version\_\_ to VERSION

## 1.0.1 (2021-06-15)

- [3f6da86](https://github.com/craigahobbs/schema-markdown/commit/3f6da86) - update links

## 1.0.0 (2021-06-15)

- [2164b18](https://github.com/craigahobbs/schema-markdown/commit/2164b18) - cleanup command-line tool args

- [d71d121](https://github.com/craigahobbs/schema-markdown/commit/d71d121) - export TYPE_MODEL

- [724de4f](https://github.com/craigahobbs/schema-markdown/commit/724de4f) - add missing exports

## 0.9.16 (2021-06-15)

- [829f167](https://github.com/craigahobbs/schema-markdown/commit/829f167) - update command-line tool
