# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

'''Python versions supported: >=3.6'''

# FOR INTERNAL COLLECTION USE ONLY
# The interfaces in this file are meant for use within the community.hashi_vault collection
# and may not remain stable to outside uses. Changes may be made in ANY release, even a bugfix release.
# See also: https://github.com/ansible/community/issues/539#issuecomment-780839686
# Please open an issue if you have questions about this.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.module_utils.hashi_vault._hashi_vault_common import HashiVaultAuthMethodBase, HashiVaultValueError
import os

class HashiVaultAuthMethodGithub(HashiVaultAuthMethodBase):
    '''HashiVault option group class for auth: github'''

    NAME = 'github'
    OPTIONS = ['token', 'token_path', 'mount_point']

    def __init__(self, option_adapter, warning_callback, deprecate_callback):
        super(HashiVaultAuthMethodGithub, self).__init__(option_adapter, warning_callback, deprecate_callback)

    def validate(self):
        if self._options.get_option('token') is None and self._options.get_option('token_path') is not None:
            token_filename = self._options.get_option('token_path')
            if os.path.exists(token_filename):
                if not os.path.isfile(token_filename):
                    raise HashiVaultValueError("The Github token file '%s' was found but is not a file." % token_filename)
                with open(token_filename) as token_file:
                    self._options.set_option('token', token_file.read().strip())

        if self._options.get_option('token') is None:
            raise HashiVaultValueError("No Github Token specified or discovered.")

    def authenticate(self, client, use_token=True):
        params = self._options.get_filled_options(*self.OPTIONS)
        params.pop('token_path', None)

        try:
            response = client.auth.github.login(**params)
        except (NotImplementedError, AttributeError):
            raise NotImplementedError("Github authentication requires HVAC version 0.6.3 or higher.")

        if use_token:
            client.token = response['auth']['client_token']

        return response
