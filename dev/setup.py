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

import hashlib
import logging
import pathlib
import platform
import re
import requests
import shutil
import tempfile
import os
import stat
import textwrap

import click

from . import command
from . import dirs
from . import tools

@click.command()
def setup() -> None:
    """
    Prepares the development environment.
    """
    install_buf()
    install_protoc()
    install_protoc_gen_go()
    install_protoc_gen_go_grpc()
    install_protoc_gen_openapiv2()
    install_swagger_codegen_cli()

def install_buf() -> None:
    """
    Installs the 'buf' tool.
    """
    # First check if it is already installed:
    tool = tools.BUF
    if is_installed(tool):
        return

    # Download and check the file that contains the checksums:
    checksums_artifact = f"sha256.txt"
    checksums_url = (
        f"https://github.com"
        f"/bufbuild/buf/releases/download/v{tool.version}"
        f"/{checksums_artifact}"
    )
    checksums_response = requests.get(checksums_url)
    checksums_response.raise_for_status()
    checksums_content = checksums_response.content
    expected_checksum = tool.checksums[checksums_artifact]
    actual_checksum = hashlib.sha256(checksums_content).hexdigest()
    if actual_checksum != expected_checksum:
        raise Exception(
            f"Failed to verify checksum of '{checksums_url}', expected '{expected_checksum}' "
            f"but got '{actual_checksum}"
        )

    # Get the system and machine name:
    os_name = platform.system()
    arch_name = platform.machine()

    # Extract the checksum of the artifact from the downloaded checksums:
    artifact_name = f"buf-{os_name}-{arch_name}.tar.gz"
    artifact_match = re.search(
        pattern=fr'^(?P<checksum>[0-9a-fA-F]+)\s+{artifact_name}$',
        string=checksums_content.decode("utf-8"),
        flags=re.MULTILINE,
    )
    if artifact_match is None:
        raise Exception(f"Failed to find checksum for artifact '{artifact_name}' inside '{checksums_url}")
    expected_checksum = artifact_match.group("checksum")
    logging.info(f"Expected checksum for artifact '{artifact_name}' is '{expected_checksum}'")

    # Create a temporary directory for the downloaded files:
    tmp_dir = pathlib.Path(tempfile.mkdtemp())
    try:
        # Download the artifact and verify its checksum:
        artifact_url = (
            f"https://github.com"
            f"/bufbuild/buf/releases/download/v{tool.version}"
            f"/{artifact_name}"
        )
        artifact_file = tmp_dir / artifact_name
        command.run(
            args=[
                "curl",
                "--location",
                "--silent",
                "--fail",
                "--output", str(artifact_file),
                artifact_url,
            ],
            check=True,
        )
        checksum_file = tmp_dir / f"{artifact_name}.txt"
        with open(file=checksum_file, encoding="utf-8", mode="w") as file:
            file.write(f"{expected_checksum} {artifact_file}\n")
        command.run(
            args=["sha256sum", "--check", str(checksum_file)],
            check=True,
        )

        # Extract the tool from the artifact:
        local_dir = dirs.local()
        if not local_dir.exists():
            local_dir.mkdir(parents=True)
        command.run(
            args=[
                "tar",
                "--directory", str(local_dir),
                "--extract",
                "--file", str(artifact_file),
                "--strip-components", "1",
            ],
            check=True,
        )
    finally:
        shutil.rmtree(tmp_dir)

def install_protoc() -> None:
    """
    Installs the protocol buffers compiler.
    """
    # First check if it is already installed and if it is the correct version:
    tool = tools.PROTOC
    if is_installed(tool):
        return

    # Download, verify and install it from the GitHub releases page:
    logging.info(f"Installing version '{tool.version}' of '{tool.name}'")
    os_name = platform.system().lower()
    arch_name = platform.machine().lower()
    tmp_dir = pathlib.Path(tempfile.mkdtemp())
    try:
        zip_name = f"protoc-{tool.version}-{os_name}-{arch_name}.zip"
        zip_url = (
            f"https://github.com"
            f"/protocolbuffers/protobuf/releases/download/v{tool.version}"
            f"/{zip_name}"
        )
        zip_file = tmp_dir / zip_name
        command.run(
            args=[
                "curl",
                "--location",
                "--silent",
                "--fail",
                "--output", str(zip_file),
                zip_url,
            ],
            check=True,
        )
        checksum_value = tool.checksums[zip_name]
        checsum_file = tmp_dir / f"{zip_name}.txt"
        with open(file=checsum_file, encoding="utf-8", mode="w") as file:
            file.write(f"{checksum_value} {zip_file}\n")
        command.run(
            args=["sha256sum", "--check", str(checsum_file)],
            check=True,
        )
        command.run(
            args=["unzip", "-d", str(dirs.local()), "-o", str(zip_file)],
            check=True,
        )
    finally:
        shutil.rmtree(tmp_dir)

def install_protoc_gen_go() -> None:
    """
    Installs the protoc plugin that generates Go code.
    """
    # Check if it is already installed and if it is the correct version:
    tool = tools.PROTOC_GEN_GO
    if is_installed(tool):
        return

    # Install the tool:
    logging.info(f"Installing version '{tool.version}' of '{tool.name}'")
    go_install(
        tool="google.golang.org/protobuf/cmd/protoc-gen-go",
        version=tool.version,
    )

def install_protoc_gen_go_grpc() -> None:
    """
    Installs the protoc plugin that generates Go gRPC code.
    """
    # Check if it is already installed and if it is the correct version:
    tool = tools.PROTOC_GEN_GO_GRPC
    if is_installed(tool):
        return

    # Install the tool:
    go_install(
        tool="google.golang.org/grpc/cmd/protoc-gen-go-grpc",
        version=tool.version,
    )

def install_protoc_gen_openapiv2() -> None:
    """
    Installs the 'protoc-gen-openapiv2' tool.
    """
    # First check if it is already installed:
    tool = tools.PROTOC_GEN_OPENAPIV2
    if is_installed(tool):
        return

    # Download and check the file that contains the checksums:
    checksums_artifact = f"grpc-gateway_{tool.version}_checksums.txt"
    checksums_url = (
        f"https://github.com"
        f"/grpc-ecosystem/grpc-gateway/releases/download/v{tool.version}"
        f"/{checksums_artifact}"
    )
    checksums_response = requests.get(checksums_url)
    checksums_response.raise_for_status()
    checksums_content = checksums_response.content
    expected_checksum = tool.checksums[checksums_artifact]
    actual_checksum = hashlib.sha256(checksums_content).hexdigest()
    if actual_checksum != expected_checksum:
        raise Exception(
            f"Failed to verify checksum of '{checksums_url}', expected '{expected_checksum}' "
            f"but got '{actual_checksum}"
        )

    # Get the system and machine name:
    os_name = platform.system().lower()
    arch_name = platform.machine().lower()

    # Extract the checksum of the artifact from the downloaded checksums:
    artifact_name = f"protoc-gen-openapiv2-v{tool.version}-{os_name}-{arch_name}"
    if os_name == "windows":
        artifact_name += ".exe"
    artifact_match = re.search(
        pattern=fr'^(?P<checksum>[0-9a-fA-F]+)\s+{artifact_name}$',
        string=checksums_content.decode("utf-8"),
        flags=re.MULTILINE,
    )
    if artifact_match is None:
        raise Exception(f"Failed to find checksum for artifact '{artifact_name}' inside '{checksums_url}")
    expected_checksum = artifact_match.group("checksum")
    logging.info(f"Expected checksum for artifact '{artifact_name}' is '{expected_checksum}'")

    # Create a temporary directory for the downloaded files:
    tmp_dir = pathlib.Path(tempfile.mkdtemp())
    try:
        # Download the artifact and verify its checksum:
        artifact_url = (
            "https://github.com"
            f"/grpc-ecosystem/grpc-gateway/releases/download/v{tool.version}"
            f"/{artifact_name}"
        )
        artifact_file = tmp_dir / artifact_name
        command.run(
            args=[
                "curl",
                "--location",
                "--silent",
                "--fail",
                "--output", str(artifact_file),
                artifact_url,
            ],
            check=True,
        )
        checksum_file = tmp_dir / f"{artifact_name}.txt"
        with open(file=checksum_file, encoding="utf-8", mode="w") as file:
            file.write(f"{expected_checksum} {artifact_file}\n")
        command.run(
            args=["sha256sum", "--check", str(checksum_file)],
            check=True,
        )

        # Move the binary to the local binaries directory:
        bin_dir = dirs.local_bin()
        if not bin_dir.exists():
            bin_dir.mkdir(parents=True)
        bin_file = bin_dir / tool.name
        shutil.move(artifact_file, bin_file)
        bin_stat = bin_file.stat()
        bin_file.chmod(bin_stat.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        if not os.access(bin_file, os.X_OK):
            bin_file.chmod()
    finally:
        shutil.rmtree(tmp_dir)

def install_swagger_codegen_cli() -> None:
    """
    Installs the 'swagger_codegen_cli' tool. Note that this tool is written in Java, so no binary is provided. We
    generate a wrapper shell script during the installation.
    """
    # First check if it is already installed:
    tool = tools.SWAGGER_CODEGEN_CLI
    if is_installed(tool):
        return

    # Check that Java is available:
    java_path = shutil.which("java")
    if java_path is None:
        raise Exception(f"Failed to find installed 'java'")

    # Create a temporary directory for the downloaded files:
    tmp_dir = pathlib.Path(tempfile.mkdtemp())
    try:
        # Download the artifact and verify its checksum:
        jar_name = f"{tool.name}-{tool.version}.jar"
        jar_url = (
            f"https://repo1.maven.org/maven2"
            f"/io/swagger/codegen/v3/{tool.name}/{tool.version}"
            f"/{jar_name}"
        )
        jar_file = tmp_dir / jar_name
        command.run(
            args=[
                "curl",
                "--location",
                "--silent",
                "--fail",
                "--output", str(jar_file),
                jar_url,
            ],
            check=True,
        )
        expected_checksum = tool.checksums[jar_name]
        checksum_file = tmp_dir / f"{jar_name}.txt"
        with open(file=checksum_file, encoding="utf-8", mode="w") as file:
            file.write(f"{expected_checksum} {jar_file}\n")
        command.run(
            args=["sha256sum", "--check", str(checksum_file)],
            check=True,
        )

        # Move the jar file to the local libraries directory:
        lib_dir = dirs.local_lib()
        if not lib_dir.exists():
            lib_dir.mkdir(parents=True)
        lib_file = lib_dir / tool.name
        shutil.move(jar_file, lib_file)

        # Create the wrapper script:
        script_text = textwrap.dedent(f"""\
        #!/bin/sh
        exec java -jar "{lib_file.absolute()}" $@
        """)
        bin_dir = dirs.local_bin()
        if not bin_dir.exists():
            bin_dir.mkdir(parents=True)
        script_file = bin_dir / tool.name
        with open(script_file, "w") as script_fd:
            script_fd.write(script_text)
        script_stat = script_file.stat()
        script_file.chmod(script_stat.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    finally:
        shutil.rmtree(tmp_dir)

def go_install(
    tool: str,
    version: str | None = None,
) -> None:
    """
    Uses the 'go install' command to install the given tool.

    The tool parameter is the complete Go path of the binary. For example, for the 'ginkgo' tool
    the value should be 'github.com/onsi/ginkgo/v2/ginkgo'.

    The version is required when the tool isn't a dependency of the project. For example, the
    'mockgen' command isn't usually a dependency of the project because the mock code that it
    generates doesn't depend on the mock generation code itself. In those cases the version
    can't be extracted from the 'go.mod' file, so it needs to be provided explicitly.
    """
    # Find the name of the binary. Note that usually the name of the binary will be the
    # last segment of the package path, but that last segment can also be a version number like
    # `v5`. In that case we need to ignore it and use the previous segment.
    segments = tool.split("/")
    name = segments[-1]
    if re.match(r"^v\d+$", name):
        name = segments[-2]

    # If the version hasn't been specified we need to extract it from the dependencies. Note that
    # we need to try with the complete package path, and then with the parent, so on. That is
    # because we don't know what part of the path corresponds to the Go module.
    if version is None:
        for i in range(len(segments), 1, -1):
            package = "/".join(segments[0:i])
            code, version = command.eval(
                args=["go", "list", "-f", "{{.Version}}", "-m", package],
            )
            if code == 0:
                break
        if version is None:
            raise Exception(f"Failed to find version for tool '{tool}'")
        logging.info(f"Version of '{tool}' is '{version}'")

    # Add the 'v' prefix if needed:
    if not version.startswith("v"):
            version = f"v{version}"

    # Try to install:
    command.run(
        args=["go", "install", f"{tool}@{version}"],
        check=True,
    )

def is_installed(tool: tools.Tool) -> bool:
    """
    Checks if the given tool is already installed.
    """
    installed_path = shutil.which(tool.name)
    if installed_path is not None:
        tool_code, tool_out = command.eval(args=tool.version_command)
        if tool_code != 0:
            raise Exception(f"Failed to find version of installed '{tool.name}'")
        version_match = re.search(
            pattern=tool.version_pattern,
            string=tool_out,
            flags=re.MULTILINE,
        )
        if version_match is None:
            raise Exception(f"Failed to find version of installed '{tool.name}'")
        installed_version = version_match.group("version")
        if installed_version == tool.version:
            logging.info(
                f"Version {tool.version} of '{tool.name}' is already installed at '{installed_path}'"
            )
            return True
        logging.info(
            f"Found '{tool.name}' already installed at '{installed_path}', but version is '{installed_version}' "
            f"instead of '{tool.version}'"
        )
        return False
