# Copyright 2018, Matt Martz <matt@sivel.net>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import os
import json

import pytest

from ansible.parsing.ajson import AnsibleJSONEncoder, AnsibleJSONDecoder
from ansible.parsing.yaml.objects import AnsibleVaultEncryptedUnicode
from ansible.utils.unsafe_proxy import AnsibleUnsafeText


def test_AnsibleJSONDecoder_vault():
    with open(os.path.join(os.path.dirname(__file__), 'fixtures/ajson.json')) as f:
        data = json.load(f, cls=AnsibleJSONDecoder)

    assert isinstance(data['password'], AnsibleVaultEncryptedUnicode)
    assert isinstance(data['bar']['baz'][0]['password'], AnsibleVaultEncryptedUnicode)
    assert isinstance(data['foo']['password'], AnsibleVaultEncryptedUnicode)

def test_encode_decode_unsafe():
    data = {
        'key_value': AnsibleUnsafeText(u'{#NOTACOMMENT#}'),
        'list': [AnsibleUnsafeText(u'{#NOTACOMMENT#}')],
        'list_dict': [{'key_value': AnsibleUnsafeText(u'{#NOTACOMMENT#}')}]}
    json_expected = (
        '{"key_value": {"__ansible_unsafe": "{#NOTACOMMENT#}"}, '
        '"list": [{"__ansible_unsafe": "{#NOTACOMMENT#}"}], '
        '"list_dict": [{"key_value": {"__ansible_unsafe": "{#NOTACOMMENT#}"}}]}'
    )
    assert json.dumps(data, cls=AnsibleJSONEncoder, preprocess_unsafe=True, sort_keys=True) == json_expected
    assert json.loads(json_expected, cls=AnsibleJSONDecoder) == data
