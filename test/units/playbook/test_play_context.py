# (c) 2012-2014, Michael DeHaan <michael.dehaan@gmail.com>
# (c) 2017 Ansible Project
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import annotations

import pytest

from ansible import constants as C
from ansible import context
from ansible.cli.arguments import option_helpers as opt_help
from ansible.playbook.play_context import PlayContext
from ansible.playbook.play import Play
from ansible.utils import context_objects as co


@pytest.fixture
def parser():
    parser = opt_help.create_base_parser('testparser')

    opt_help.add_runas_options(parser)
    opt_help.add_meta_options(parser)
    opt_help.add_runtask_options(parser)
    opt_help.add_vault_options(parser)
    opt_help.add_async_options(parser)
    opt_help.add_connect_options(parser)
    opt_help.add_subset_options(parser)
    opt_help.add_check_options(parser)
    opt_help.add_inventory_options(parser)

    return parser


@pytest.fixture
def reset_cli_args():
    co.GlobalCLIArgs._Singleton__instance = None
    yield
    co.GlobalCLIArgs._Singleton__instance = None


def test_play_context(mocker, parser, reset_cli_args):
    options = parser.parse_args(['-vv', '--check'])
    context._init_global_context(options)
    play = Play.load({})
    play_context = PlayContext(play=play)

    assert play_context.remote_addr is None
    assert play_context.remote_user is None
    assert play_context.password == ''
    assert play_context.private_key_file == C.DEFAULT_PRIVATE_KEY_FILE
    assert play_context.timeout == C.DEFAULT_TIMEOUT
    assert getattr(play_context, 'verbosity', None) is None
    assert play_context.check_mode is True

    mock_play = mocker.MagicMock()
    mock_play.force_handlers = True

    play_context = PlayContext(play=mock_play)
    assert play_context.force_handlers is True

    mock_task = mocker.MagicMock()
    mock_task.connection = 'mocktask'
    mock_task.remote_user = 'mocktask'
    mock_task.port = 1234
    mock_task.no_log = True
    mock_task.become = True
    mock_task.become_method = 'mocktask'
    mock_task.become_user = 'mocktaskroot'
    mock_task.become_pass = 'mocktaskpass'
    mock_task._local_action = False
    mock_task.delegate_to = None

    all_vars = dict(
        ansible_connection='mock_inventory',
        ansible_ssh_port=4321,
    )

    mock_templar = mocker.MagicMock()

    play_context = PlayContext()
    play_context = play_context.set_task_and_variable_override(task=mock_task, variables=all_vars, templar=mock_templar)

    assert play_context.connection == 'mock_inventory'
    assert play_context.remote_user == 'mocktask'
    assert play_context.no_log is True

    mock_task.no_log = False
    play_context = play_context.set_task_and_variable_override(task=mock_task, variables=all_vars, templar=mock_templar)
    assert play_context.no_log is False


@pytest.mark.parametrize('delegated_host_vars, expected_remote_addr, expected_ansible_host', [
    pytest.param({}, 'delegated.example.com', 'delegated.example.com', id='unset'),
    pytest.param({'ansible_host': None}, 'delegated.example.com', 'delegated.example.com', id='none'),
    pytest.param({'ansible_host': None, 'ansible_ssh_host': '10.0.0.2'}, '10.0.0.2', None, id='none_with_ssh_host'),
    pytest.param({'ansible_host': '10.0.0.1'}, '10.0.0.1', '10.0.0.1', id='set'),
])
def test_play_context_delegated_remote_addr(mocker, delegated_host_vars, expected_remote_addr, expected_ansible_host):
    mock_task = mocker.MagicMock()
    mock_task.delegate_to = 'delegated.example.com'
    mock_task.remote_user = None
    mock_task.check_mode = None
    mock_task.diff = None

    delegated_vars = dict(delegated_host_vars, inventory_hostname='localhost')
    all_vars = dict(inventory_hostname='localhost', ansible_delegated_vars={'delegated.example.com': delegated_vars})

    play_context = PlayContext().set_task_and_variable_override(task=mock_task, variables=all_vars, templar=mocker.MagicMock())

    assert play_context.remote_addr == expected_remote_addr
    # TaskExecutor resolves connection options from these same delegated vars
    assert delegated_vars.get('ansible_host') == expected_ansible_host
