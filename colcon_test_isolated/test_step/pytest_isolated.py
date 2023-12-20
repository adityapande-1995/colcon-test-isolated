from colcon_core.task.python.test.pytest import *
from pathlib import Path

current_dir = Path(__file__).parent
isolate_file = str(current_dir / "isolate.py")

class PytestIsolatedPythonTestingStep(PytestPythonTestingStep):

    async def step(self, context, env, setup_py_data):
        print("Isolating the test")
        cmd = [sys.executable, isolate_file, sys.executable, '-m', 'pytest']
        junit_xml_path = Path(
            context.args.test_result_base
            if context.args.test_result_base
            else context.args.build_base) / 'pytest.xml'
        # avoid using backslashes in the PYTEST_ADDOPTS env var on Windows
        args = [
            '--tb=short',
            '--junit-xml=' + str(PurePosixPath(*junit_xml_path.parts)),
            '--junit-prefix=' + context.pkg.name,
        ]
        # use -o option only when available
        # https://github.com/pytest-dev/pytest/blob/3.3.0/CHANGELOG.rst
        from pytest import __version__ as pytest_version
        if Version(pytest_version) >= Version('3.3.0'):
            args += [
                '-o', 'cache_dir=' + str(PurePosixPath(
                    *(Path(context.args.build_base).parts)) / '.pytest_cache'),
            ]
        env = dict(env)

        if (
            context.args.pytest_with_coverage or
            has_test_dependency(setup_py_data, 'pytest-cov')
        ):
            try:
                from pytest_cov import __version__ as pytest_cov_version
            except ImportError:
                logger.warning(
                    'Test coverage will not be produced for package '
                    f"'{context.pkg.name}' since the pytest extension 'cov' "
                    'was not found')
            else:
                args += [
                    '--cov=' + str(PurePosixPath(
                        *(Path(context.args.path).parts))),
                    '--cov-report=html:' + str(PurePosixPath(
                        *(Path(context.args.build_base).parts)) /
                        'coverage.html'),
                    '--cov-report=xml:' + str(PurePosixPath(
                        *(Path(context.args.build_base).parts)) /
                        'coverage.xml'),
                ]
                # use --cov-branch option only when available
                # https://github.com/pytest-dev/pytest-cov/blob/v2.5.0/CHANGELOG.rst
                if Version(pytest_cov_version) >= Version('2.5.0'):
                    args += [
                        '--cov-branch',
                    ]
                else:
                    logger.warning(
                        'Test coverage will be produced but will not contain '
                        'branch coverage information because the pytest '
                        "extension 'cov' does not support it (need 2.5.0, "
                        f'have {pytest_cov_version})')
                env['COVERAGE_FILE'] = os.path.join(
                    context.args.build_base, '.coverage')

        if context.args.retest_until_fail:
            try:
                import pytest_repeat  # noqa: F401
            except ImportError:
                logger.warning(
                    "Ignored '--retest-until-fail' for package "
                    f"'{context.pkg.name}' since the pytest extension "
                    "'repeat' was not found")
            else:
                count = context.args.retest_until_fail + 1
                args += [f'--count={count}']

        if context.args.retest_until_pass:
            try:
                import pytest_rerunfailures  # noqa: F401
            except ImportError:
                logger.warning(
                    "Ignored '--retest-until-pass' for package "
                    f"'{context.pkg.name}' since pytest extension "
                    "'rerunfailures' was not found")
            else:
                args += [f'--reruns={context.args.retest_until_pass}']

        if context.args.pytest_args is not None:
            args += context.args.pytest_args

        if args:
            env['PYTEST_ADDOPTS'] = ' '.join(
                a if ' ' not in a else f'"{a}"'
                for a in args)

        # create dummy result in case the invocation fails early
        # and doesn't generate a result file at all
        junit_xml_path.parent.mkdir(parents=True, exist_ok=True)
        junit_xml_path.write_text(f"""<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="{context.pkg.name}" tests="1" failures="0" time="0" errors="1" skipped="0">
  <testcase classname="{context.pkg.name}" name="pytest.missing_result" time="0">
    <failure message="The test invocation failed without generating a result file."/>
  </testcase>
</testsuite>
""")  # noqa: E501

        completed = await run(
            context, cmd, cwd=context.args.path, env=env)

        # use local import to avoid a dependency on pytest
        try:
            from _pytest.main import ExitCode
            EXIT_CODE_TESTS_FAILED = ExitCode.TESTS_FAILED  # noqa: N806
        except ImportError:
            # support pytest < 5.0
            from _pytest.main import EXIT_TESTSFAILED
            EXIT_CODE_TESTS_FAILED = EXIT_TESTSFAILED  # noqa: N806
        if completed.returncode == EXIT_CODE_TESTS_FAILED:
            context.put_event_into_queue(
                TestFailure(context.pkg.name))

        try:
            from _pytest.main import ExitCode
            EXIT_CODE_NO_TESTS = ExitCode.NO_TESTS_COLLECTED  # noqa: N806
        except ImportError:
            # support pytest < 5.0
            from _pytest.main import EXIT_NOTESTSCOLLECTED
            EXIT_CODE_NO_TESTS = EXIT_NOTESTSCOLLECTED  # noqa: N806
        if completed.returncode not in (
            EXIT_CODE_NO_TESTS, EXIT_CODE_TESTS_FAILED
        ):
            return completed.returncode
        

