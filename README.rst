colcon-test-isolated
================

An extension for `colcon-core <https://github.com/colcon/colcon-core>`_ to be used for isolating test cases based on linux network namespaces.

## Usage 
For now, I'm hoping to get this working like :
```
colcon test --packages-select <you-pytest-pkg, like colcon-core> --python-testing isolated
```

Currently, colcon supports ``pytest`` and ``unittest``.
This third keyword ``isolate`` extends the ``pytest`` action, by running it with the ``isolate`` executable.

