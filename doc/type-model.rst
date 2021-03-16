Type Model
==========

At the heart of Schema Markdown is the **type model**. The type model is a dictionary object that
maps schema type names to schema type definitions. The :ref:`schema-markdown:Schema Markdown`
definition of type model is shown below:

.. include:: ../build/doc/type_model.smd
   :code: text

If needed, the compiled type model can be imported as follows:

.. code-block:: python

  from schema_markdown.type_model import TYPE_MODEL
