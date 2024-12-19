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

from ansible.module_utils.hashi_vault._hashi_vault_common import HashiVaultAuthMethodBase


class HashiVaultAuthMethodRadius(HashiVaultAuthMethodBase):
    '''HashiVault option group class for auth: radius'''

    NAME = 'radius'
    OPTIONS = ['username', 'password', 'mount_point']

    def __init__(self, option_adapter, warning_callback, deprecate_callback):
        super(HashiVaultAuthMethodRadius, self).__init__(option_adapter, warning_callback, deprecate_callback)

    def validate(self):
        self.validate_by_required_fields('username', 'password')

    def authenticate(self, client, use_token=True):
        params = self._options.get_filled_options(*self.OPTIONS)
        try:
            response = client.auth.radius.login(**params)
        except (NotImplementedError, AttributeError):
            raise NotImplementedError("Radius authentication requires HVAC version 0.9.0 or higher.")

        if use_token:
            client.token = response['auth']['client_token']

        return response
