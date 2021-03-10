;;; smd-mode.el --- major mode for editing Schema Markdown

;; Version: 0.1

;;; Commentary:

;; To install, add the following to your .emacs file:

;; (package-initialize)
;;
;; (unless (package-installed-p 'smd-mode)
;;   (let ((smd-mode-file (make-temp-file "smd-mode")))
;;     (url-copy-file "https://raw.githubusercontent.com/craigahobbs/schema-markdown/master/extra/smd-mode.el" smd-mode-file t)
;;     (package-install-file smd-mode-file)
;;     (delete-file smd-mode-file)))
;; (add-to-list 'auto-mode-alist '("\\.smd?\\'" . smd-mode))

;;; Code:
(require 'generic-x)

;;;###autoload
(define-generic-mode 'smd-mode
      '("#")
      '(
        "action"
        "enum"
        "errors"
        "group"
        "input"
        "nullable"
        "optional"
        "output"
        "path"
        "query"
        "struct"
        "typedef"
        "union"
        "urls"
        )
      (list
       (cons
        (regexp-opt
         '(
           "bool"
           "date"
           "datetime"
           "float"
           "int"
           "object"
           "string"
           "uuid"
           ) 'words) 'font-lock-type-face)
        )
      '(".smd\\'")
      nil
      "Major mode for editing Schema Markdown")

(provide 'smd-mode)
;;; smd-mode.el ends here
