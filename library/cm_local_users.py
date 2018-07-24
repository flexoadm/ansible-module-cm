#!/usr/bin/env python
# -*- coding: utf-8 -*-

# (c) 2017, Sergey Buyalsky <sergey.buyalsky@onefactor.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

DOCUMENTATION = '''
---
module: cm_local_users
author: "Sergey Buyalsky (@flexoadm)"
version_added: "0.1"
short_description: Manage kerberos user accounts
requirements: [ kadmin.local ]
description:
    - Manage kerberos user accounts and attributes. 
      The module can be used only on host with krb5kdc installed and with kadmin.local tool.
options:
    state:
        required: false
        default: "present"
        choices: [ "present", "absent", "change" ]
        description:
            - Whether the account should exist or not, taking action if the state is different from what is stated.
    name:
        required: true
        description:
            - Name of the user to create or remove.
    instance:
        required: false
        description:
            - Host/hostname or group.
    realm:
        required: false
        description:
            - Use realm as the default database realm.
    password:
        required: false
    attributes:
        required: false
        description:
            - Attributes of principal separated by comma.
'''

EXAMPLES = '''
# Add the user 'test' with a random password
- kbr5_princ:
    state: present
    name: "test"

# Add the user 'test' with a password
- kbr5_princ:
    state: present
    name: "test"
    password: "123123"

# Add the user 'test' with a realm and a instance
- kbr5_princ:
    state: present
    name: "test"
    instance: "admin"
    realm: "EXAMPLE.LOCAL"

# Remove the user 'test'
- krb5_princ:
    state: absent
    name: "test"

# Change password the user 'test'
- krb5_princ:
    state: change
    name: "test"
    password: "pass"

# Random password the user 'test'
- krb5_princ:
    state: change
    name: "test"
    password: ""
'''

from cm_api.api_client import ApiResource, ApiException, API_CURRENT_VERSION
from cm_api.endpoints import users
import json
from ansible.module_utils.basic import AnsibleModule


def add_user(module):

    cm_host = "test-cm.corp.onefactor.com"
    api = ApiResource(cm_host, username="test", password="test", use_tls=True, version=12)

    name = module.params.get('name')
    password = module.params.get('password')
    role = module.params.get('role')

    if role is 'admin':
        role = ['ROLE_ADMIN']
    else:
        role = ['ROLE_USER']

    result = users.create_user(api, name, password, role)

    # if stderr:
    #     if "Principal or policy already exists while creating" in stderr:
    #         result = json.dumps({
    #             "changed": False,
    #             "msg": "User " + name + " already is created"
    #         })
    #     else:
    #         result = json.dumps({
    #             "failed": True,
    #             "changed": False,
    #             "msg": stderr
    #         })
    # else:
    #     result = json.dumps({
    #         "changed": True,
    #         "msg": "User was created"
    #     })
    # print(result)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default='present', choices=['present', 'absent']),
            name=dict(required=True),
            password=dict(required=True),
            role=dict(required=True, default='user', choices=['admin', 'user'])
        )
    )

    if module.params.get('state') == "present":
        add_user(module)
    # if module.params.get('state') == "absent":
    #     remove_user(module)


if __name__ == '__main__':
    main()