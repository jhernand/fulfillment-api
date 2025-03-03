# -*- coding: utf-8 -*-

#
# Copyright (c) 2025 Red Hat Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License
# is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied. See the License for the specific language governing permissions and limitations under
# the License.
#

import json

def yaml() -> str:
    """
    Generates the content of the 'buf.yaml' file.
    """
    return json.dumps({
        "version": "v2",
        "lint": {
            "use": [
                "STANDARD",
            ],
            "except": [
                "ENUM_VALUE_PREFIX",
                "SERVICE_SUFFIX",
            ],
            "enum_zero_value_suffix": "UNSPECIFIED",
            "ignore": [
                "proto/google",
            ],
        },
        "breaking": {
            "use": [
                "FILE",
            ],
        },
        "modules": [
            {
                "path": "proto",
            },
        ],
    })

def gen_yaml(out_dir: str) -> str:
    """
    Generates the content of the 'buf.gen.yaml' file.
    """
    return json.dumps({
        "version":"v1",
        "managed": {
            "enabled": True,
            "go_package_prefix": {
                "default": "github.com/innabox/fulfillment-api",
            },
        },
        "plugins": [
            {
                "plugin": "openapiv2",
                "strategy": "all",
                "out": str(out_dir),
                "opt": [
                    "allow_merge",
                    "json_names_for_fields=false",
              ]
           },
        ],
    })