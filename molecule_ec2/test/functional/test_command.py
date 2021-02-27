#  Copyright (c) 2015-2018 Cisco Systems, Inc.
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.

import os

import pytest
import sh
import functools

from molecule import logger, util
from molecule.test.conftest import change_dir_to

pytest_plugins = [
    "helpers_namespace",
    "html",
    "mock",
    "plus",
    "verbose-parametrize",
    "dependency",
]

LOG = logger.get_logger(__name__)


@pytest.helpers.register
@pytest.fixture
def with_scenario(scenario_name):
    scenario_directory = os.path.join(
        os.path.dirname(util.abs_path(__file__)), os.path.pardir, "scenarios/driver/ec2"
    )

    with change_dir_to(scenario_directory):
        yield
        if scenario_name:
            msg = "CLEANUP: Destroying instances for all scenario(s)"
            LOG.info(msg)
            options = {"driver_name": "ec2", "all": True}
            cmd = sh.molecule.bake("destroy", **options)
            pytest.helpers.run_command(cmd)


@pytest.helpers.register
@pytest.fixture
def scenario_name(request):
    try:
        return request.param
    except AttributeError:
        return None


@pytest.helpers.register
@pytest.fixture
def driver_name():
    return "ec2"


def std_parametrize(func):
    # Bundle up parametrize to avoid repetition
    @pytest.mark.extensive
    @pytest.mark.parametrize(
        "scenario_name", [("default"), ("multi-node")], indirect=["scenario_name"]
    )
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapped


@std_parametrize
def test_command_check(with_scenario, scenario_name):
    options = {"scenario_name": scenario_name}
    cmd = sh.molecule.bake("check", **options)
    pytest.helpers.run_command(cmd)


@std_parametrize
def test_command_cleanup(with_scenario, scenario_name):
    options = {"scenario_name": scenario_name}
    cmd = sh.molecule.bake("cleanup", **options)
    pytest.helpers.run_command(cmd)


@std_parametrize
def test_command_converge(with_scenario, scenario_name):
    options = {"scenario_name": scenario_name}
    cmd = sh.molecule.bake("converge", **options)
    pytest.helpers.run_command(cmd)


@std_parametrize
def test_command_create(with_scenario, scenario_name):
    options = {"scenario_name": scenario_name}
    cmd = sh.molecule.bake("create", **options)
    pytest.helpers.run_command(cmd)


@std_parametrize
def test_command_destroy(with_scenario, scenario_name):
    options = {"scenario_name": scenario_name}
    cmd = sh.molecule.bake("destroy", **options)
    pytest.helpers.run_command(cmd)


@std_parametrize
def test_command_idempotence(with_scenario, scenario_name):
    pytest.helpers.idempotence(scenario_name)


def test_command_init_role(temp_dir):
    pytest.helpers.init_role(temp_dir, "ec2")


@pytest.mark.xfail(reason="https://github.com/ansible-community/molecule/issues/2797")
def test_command_init_scenario(temp_dir):
    pytest.helpers.init_scenario(temp_dir, "ec2")


@std_parametrize
def test_command_lint(with_scenario, scenario_name):
    options = {"scenario_name": scenario_name}
    cmd = sh.molecule.bake("lint", **options)
    pytest.helpers.run_command(cmd)


def test_command_list(with_scenario):
    expected = """
Instance Name    Driver Name    Provisioner Name    Scenario Name    Created    Converged
---------------  -------------  ------------------  ---------------  ---------  -----------
instance         ec2            ansible             default          false      false
instance-1       ec2            ansible             multi-node       false      false
instance-2       ec2            ansible             multi-node       false      false
""".strip()

    pytest.helpers.list(expected)


def test_command_list_with_format_plain(with_scenario):
    expected = """
instance    ec2  ansible  default     false  false
instance-1  ec2  ansible  multi-node  false  false
instance-2  ec2  ansible  multi-node  false  false
""".strip()
    pytest.helpers.list_with_format_plain(expected)


@pytest.mark.extensive
@pytest.mark.parametrize(
    "scenario_name, login_args",
    [
        # login_args: instance, regex
        ("default", [["instance", ".*Welcome to Ubuntu 16.04.*"]]),
        (
            "multi-node",
            [
                ["instance-1", ".*Welcome to Ubuntu 16.04.*"],
                ["instance-2", ".*Welcome to Ubuntu 16.04.*"],
            ],
        ),
    ],
    indirect=["scenario_name"],
)
def test_command_login(with_scenario, scenario_name, login_args):
    pytest.helpers.login(login_args, scenario_name)


@std_parametrize
def test_command_prepare(with_scenario, scenario_name):
    options = {"scenario_name": scenario_name}

    cmd = sh.molecule.bake("create", **options)
    pytest.helpers.run_command(cmd)

    cmd = sh.molecule.bake("prepare", **options)
    pytest.helpers.run_command(cmd)


@std_parametrize
def test_command_side_effect(with_scenario, scenario_name):
    options = {"scenario_name": scenario_name}
    cmd = sh.molecule.bake("side-effect", **options)
    pytest.helpers.run_command(cmd)


@std_parametrize
def test_command_syntax(with_scenario, scenario_name):
    options = {"scenario_name": scenario_name}
    cmd = sh.molecule.bake("syntax", **options)
    pytest.helpers.run_command(cmd)


@std_parametrize
def test_command_test(with_scenario, scenario_name):
    pytest.helpers.test(driver_name, scenario_name)


@std_parametrize
def test_command_verify(with_scenario, scenario_name):
    pytest.helpers.verify(scenario_name)
