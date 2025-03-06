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

import click

from . import command
from . import tools

@click.command()
@click.option(
    "--check-only",
    is_flag=True,
    help="Check the format, but don't fix it.",
)
def format(check_only: bool) -> None:
    """
    Formats the source code.
    """
    args = [tools.BUF.name, "format"]
    if check_only:
        args.extend([
            "--diff",
            "--exit-code",
        ])
    else:
        args.extend([
            "--write",
        ])
    command.run(
        args=args,
        check=True,
    )
