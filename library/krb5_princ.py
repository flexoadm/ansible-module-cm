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
module: krb5_princ
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

import subprocess
import json
from ansible.module_utils.basic import AnsibleModule


def concate_name(name, instance, realm):
    name = "{}{}{}".format(name, "/{}".format(instance) if instance else "", "@{}".format(realm) if realm else "")
    return name


def principal_add(module):

    name = module.params.get('name')
    instance = module.params.get('instance')
    realm = module.params.get('realm')
    password = module.params.get('password')
    attributes = module.params.get('attributes')

    name = concate_name(name, instance, realm)
    args = []

    if attributes:
        args.append(attributes)

    cmd_pass = '-randkey'
    if not password:
        args.append(cmd_pass)
    else:
        cmd_pass = '-pw'
        args.append(cmd_pass)
        args.append(password)

    args.append(name)

    str_args = [str(x) for x in args]

    process = subprocess.Popen(['kadmin.local', 'add_principal'] + str_args, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, shell=False)
    stdout, stderr = process.communicate()

    if stderr:
        if "Principal or policy already exists while creating" in stderr:
            result = json.dumps({
                "changed": False,
                "msg": "User " + name + " already is created"
            })
        else:
            result = json.dumps({
                "failed": True,
                "changed": False,
                "msg": stderr
            })
    else:
        result = json.dumps({
            "changed": True,
            "msg": "User was created"
        })
    print(result)


def principal_remove(module):

    name = module.params.get('name')
    instance = module.params.get('instance')
    realm = module.params.get('realm')

    name = concate_name(name, instance, realm)

    process = subprocess.Popen(['kadmin.local', 'delprinc', name], stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, shell=False)
    stdout, stderr = process.communicate()

    if stderr:
        if "Principal does not exist while deleting principal" in stderr:
            result = json.dumps({
                "changed": False,
                "msg": "User " + name + " not exist"
            })
        else:
            result = json.dumps({
                "failed": True,
                "changed": False,
                "msg": stderr
            })
    else:
        result = json.dumps({
            "changed": True,
            "msg": "User was deleted"
        })
    print(result)


def principal_change(module):
    name = module.params.get('name')
    instance = module.params.get('instance')
    realm = module.params.get('realm')
    password = module.params.get('password')

    name = concate_name(name, instance, realm)
    args = []

    cmd_pass = '-randkey'
    if not password:
        args.append(cmd_pass)
    else:
        cmd_pass = '-pw'
        args.append(cmd_pass)
        args.append(password)

    args.append(name)

    str_args = [str(x) for x in args]

    process = subprocess.Popen(['kadmin.local', 'change_password'] + str_args, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, shell=False)
    stdout, stderr = process.communicate()

    if stderr:
        result = json.dumps({
            "failed": True,
            "changed": False,
            "msg": stderr
        })
    else:
        result = json.dumps({
            "changed": True,
            "msg": "Password was changed"
        })
    print(result)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default='present', choices=['present', 'absent', 'change']),
            name=dict(required=True),
            instance=dict(required=False),
            realm=dict(required=False),
            password=dict(required=False),
            attributes=dict(required=False)
        )
    )
    if module.params.get('state') == "present":
        principal_add(module)
    if module.params.get('state') == "absent":
        principal_remove(module)
    if module.params.get('state') == "change":
        principal_change(module)

if __name__ == '__main__':
    main()
