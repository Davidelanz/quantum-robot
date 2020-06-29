""""Script which creates a GitHub-compliant README.rst file."""

README = "README.rst"

def append_string(string):
    with open(README, "a") as f_out:
        f_out.write(string)


def append_file(file):
    with open(file) as f_in:
        with open(README, "a") as f_out:
            for line in f_in:
                f_out.write(line)
            f_out.write(" ")


# Initialize file
with open(README, "w") as f_out:
    f_out.write("")

# Title
#append_string("""quantum-robot
#=============
#
#""")

# Include summary
append_file("modules/summary.rst")

# Contents
append_string("""
Contents
--------

-  `Install <#install>`__
-  `Notebooks <#notebooks>`__
-  `Contributing <#contributing>`__
-  `Citing <#citing>`__
-  `License <#license>`__

""")

# Install
append_string("""
Install\ `↑ <#contents>`__
-----------------------------------------
""")

append_file("modules/install.rst")

append_string("""
See also the `Getting Started <http://www.quantum-robot.org/docs/getting_started.html>`_.
guide.

""")

# Notebooks
append_string("""
Notebooks\ `↑ <#contents>`__
---------------------------------------

""")

append_file("modules/notebooks.rst")

# Contributing
append_string("""
Contributing `↑ <#contents>`__
---------------------------------------

""")

append_file("modules/contributing.rst")


# Citing
append_string("""
Citing `↑ <#contents>`__
---------------------------------------

""")

append_file("modules/citing.rst")


# License
append_string("""
License `↑ <#contents>`__
---------------------------------------

""")

append_file("modules/license.rst")
