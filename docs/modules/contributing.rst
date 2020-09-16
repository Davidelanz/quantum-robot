
If you are interested in the project, we welcome new contributors
of all experience levels.
For any question, `contact the maintainer <mailto:davidel96@hotmail.it>`_.

An example module with the docstring standard we adopted is available
`here <https://github.com/Davidelanz/quantum-robot/blob/master/docs/example/qrobot_doc.py>`_.

.. note::
    The documentation build workflow is the following one:
    
    1.  Modify the ``.rst`` modules in the ``docs/modules`` folder
        of the Github repository, or the high-level ``.rst`` modules 
        in the ``docs`` folder 
        (``getting_started.rst``, ``index.rst``, ``models.rst``)
    2.  Build the ``README.rst`` file with the ``readme_export.py``
        Python 3 script in the ``docs`` folder
    3.  Build the ``README_PYPI.md`` file with the ``readme_pypi_export.sh``
        bash script
    4.  Run the ``make html`` Sphinx command to build the documentation 
        HTML files