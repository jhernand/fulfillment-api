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

class Tool:
    def __init__(
        self,
        name: str,
        version: str = "",
        version_command: list[str] = [],
        version_pattern: str = "",
        checksums: dict[str, str] = {},
    ):
        # Save the values:
        self.name = name
        self.version = version
        self.version_command = version_command
        self.version_pattern = version_pattern

        # The keys of the checksums dictionary can reference the name or the version:
        self.checksums = {}
        for artifact_name, artifact_checksum in checksums.items():
            artifact_name = artifact_name.format(
                name=name,
                version=version,
            )
            self.checksums[artifact_name] = artifact_checksum

BUF = Tool(
    name="buf",
    version="1.50.0",
    version_command=["buf", "--version"],
    version_pattern=r"^(?P<version>.*)$",
    checksums={
        "sha256.txt": "736e74d1697dcf253bc60b2f0fb4389c39dbc7be68472a7d564a953df8b19d12",
    },
)

PROTOC = Tool(
    name="protoc",
    version="29.3",
    version_command=["protoc", "--version"],
    version_pattern=r"^libprotoc\s+(?P<version>.*)$",
    checksums={
        "{name}-{version}-linux-x86_64.zip": "3e866620c5be27664f3d2fa2d656b5f3e09b5152b42f1bedbf427b333e90021a",
    },
)

PROTOC_GEN_GO = Tool(
    name="protoc-gen-go",
    version="1.36.4",
    version_command=["protoc-gen-go", "--version"],
    version_pattern=r"^protoc-gen-go\s+v(?P<version>.*)$",
)

PROTOC_GEN_GO_GRPC = Tool(
    name="protoc-gen-go-grpc",
    version_command=["protoc-gen-go-grpc", "--version"],
    version_pattern=r"^protoc-gen-go-grpc\s+(?P<version>.*)$",
    version="1.5.1",
)

PROTOC_GEN_OPENAPIV2 = Tool(
    name="protoc-gen-openapiv2",
    version="2.26.1",
    version_command=["protoc-gen-openapiv2", "--version"],
    version_pattern=r"^Version\s+(?P<version>[^,]+),.*$",
    checksums={
        "grpc-gateway_{version}_checksums.txt": "577b704088b2748342563d2c59e883b5dee8148cab08966e59dda16c3981cfbe",
    },
)

SWAGGER_CODEGEN_CLI = Tool(
    name="swagger-codegen-cli",
    version="3.0.67",
    version_command=["swagger-codegen-cli", "version"],
    version_pattern=r"^(?P<version>.*)$",
    checksums={
        "{name}-{version}.jar": "7ec19718a723fd66035d2f26e76ba23dcfb623795dd51c6983b162f49ec1dd1d",
    },
)