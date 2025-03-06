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

import pathlib
import shutil
import tempfile

import click

from . import buf
from . import command
from . import dirs
from . import tools

@click.group(invoke_without_command=True)
@click.pass_context
def generate(ctx: click.Context):
    """
    Generate code.
    """
    if ctx.invoked_subcommand is not None:
        return
    ctx.invoke(openapi)

def openapi() -> None:
    """
    Generate the OpenAPI specification.
    """
    # Remove previously generated files:
    project_dir = dirs.project()
    openapi_dir = project_dir / "openapi"
    if openapi_dir.exists():
        shutil.rmtree(openapi_dir)
        openapi_dir.mkdir(parents=True)
    v2_dir = openapi_dir / "v2"
    v2_dir.mkdir(parents=True)
    v3_dir = openapi_dir / "v3"
    v3_dir.mkdir(parents=True)

    # Create a temporary directory for the downloaded files:
    tmp_dir = pathlib.Path(tempfile.mkdtemp())
    try:
        # Use the 'buf' tool to generate OpenAPI version 2. Note that we need some Go settings even if we are not going
        # to generate Go code. That is a side efect of using the gRPC gateway tool to generate the OpenAPI.
        v2_tmp_dir = tmp_dir / "v2"
        v2_tmp_dir.mkdir()
        command.run(
            args=[
                tools.BUF.name, "generate",
                "--template", buf.gen_yaml(out_dir=v2_tmp_dir),
            ],
            check=True,
        )

        # Find the generated version 2 file and move it to the destination directory:
        v2_tmp_files = list(v2_tmp_dir.glob("*.json"))
        if len(v2_tmp_files) != 1:
            raise Exception(f"Expected exactly one generated OpenAPI file, but found {len(v2_tmp_files)}")
        v2_tmp_file = v2_tmp_files[0]
        v2_file = v2_dir / "openapi.json"
        shutil.move(v2_tmp_file, v2_file)

        # Use the 'swagger-codegen-cli' tool to read the generated version 2 and write version 3:
        v3_tmp_dir = tmp_dir / "v3"
        v3_tmp_dir.mkdir()
        command.run(
            args=[
                "swagger-codegen-cli", "generate",
                "--lang", "openapi-yaml",
                "--input-spec", str(v2_file),
                "--output", str(v3_tmp_dir),
            ],
            check=True,
        )

        # Find the generated version 3 file and move it to the destination directory:
        v3_tmp_files = list(v3_tmp_dir.glob("*.yaml"))
        if len(v3_tmp_files) != 1:
            raise Exception(f"Expected exactly one generated OpenAPI file, but found {len(v3_tmp_files)}")
        v3_tmp_file = v3_tmp_files[0]
        v3_file = v3_dir / "openapi.yaml"
        shutil.move(v3_tmp_file, v3_file)
    finally:
        shutil.rmtree(tmp_dir)

