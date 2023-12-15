colcon-test-isolated
================

An extension for `colcon-core <https://github.com/colcon/colcon-core>`_ to act as a template for new extensions.

When using this template, be sure to replace all instances of the word "template" in the repository::

   $ find * -type f | xargs sed -i 's/colcon-test-isolated/colcon-package-name/g'
   $ find * -type f | xargs sed -i 's/colcon_test_isolated/colcon_package_name/g'
   $ mv colcon_test_isolated colcon_package_name
   $ grep -iR template *
