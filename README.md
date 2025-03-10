# Fulfillment API

This project contains the definition of the fulfillment API.

The API is specified using [Protocol Buffers](https://protobuf.dev) and [gRPC](https://grpc.io) definitions inside the
[`proto`](proto/fulfillment/v1) directory. For example, the definition for the `ClusterOrder` object that will be used to
request the provisioning of a cluster is inside the
[`cluster_order_type.proto`](proto/fulfillment/v1/cluster_order_type.proto) file, and the definition of the operations to
list, get, place and cancel an order are in the
[`cluster_orders_service.proto`](proto/fulfillment/v1/cluster_orders_service.proto) file.

The server will be implemented using Protocol Buffers and gRPC as well, and it will also support plain HTTP and JSON
access via the [gRPC-Gateway](https://grpc-ecosystem.github.io/grpc-gateway).

## Recommended development setup

This is an opinionated setup, the one used by the person that initially wrote this document. You can find other ways
to prepare your environment. As long as the resulting code works fine you are good.

### Make sure that you have a version 3.12 or newer of Python available

This is needed because the build tools (the `dev.py` script) of the project are written in Python and uses some recent
features that are only available in Python 3.12 or newer.

In some Linux distributions (RHEL 9, for example) the name of the Python 3.12 binary may be `python3.12`, but you need
to make sure that it is named just `python`. To do so you can, for example, create a symbolic link in your `~/bin`
directory that points to that binary:

    $ python --version
    Python 3.9.21  <-- This will not work

    $ which python3.12
    /usr/bin/python3.12

    $ ln -s ~/bin/python /usr/bin/python3.12

    $ hash -r
    $ python --version
    Python 3.12.5  <-- This will work

The `hash -r` command is needed to clear the cache that the shell keeps to avoid looking up binaries in the path
repeatedly. If your shell doesn't have that `hash` command you can close the session and start a new one.

Do the same for the `pip` command if needed:

    $ ln -s /usr/bin/pip3.12 ~/bin/pip
    $ hash -r
    $ pip --version
    pip 23.2.1 from /usr/lib/python3.12/site-packages/pip (python 3.12)

### Make sure that you have version 1.22.9 or newer of Go available

This project doesn't really contain Go project, but some of the code generation tools (`protoc-gen-openapi`, for
example) are written in Go and installed using `go install ...`. So you will need the Go compiler and tools. If your
operating system provides a recent enough version, at least 1.22.9, then you can use it directly. If not you can
download and install it manually. For example, you can install it to `~/go` with something like this:

    $ wget https://go.dev/dl/go1.22.9.linux-amd64.tar.gz
    $ tar xvf go1.22.9.linux-amd64.tar.gz

This is just an example, make sure to download the version appropriate for your operating system and architecture.

Later you will configure your environment (via the `.envrc` file ) to use that version.

### Install the `direnv` tool

Follow the instructions in the [`direnv`](https://direnv.net) page to install and enable it. This will be used to create
an environment for the project without interfering with other settings that you may need for your system or for other
projects.

### Prepare the project directory

Create a directory where you will have the files for the project, for example `~/fulfillment-api`. Note that this is
not where you will check-out the source code of the project: that will go into a `repository` sub-directory. But before
that create a `.envrc` file in that directory similar to this:

```shell
# Configure Python:
export VIRTUAL_ENV=".venv"
layout python

# Configure Go:
export GOROOT="${HOME}/go"
export GOPATH="${PWD}/.local"
export GOBIN="${PWD}/.local/bin"
PATH_add "${GOROOT}/bin"
PATH_add "${PWD}/.local/bin"
```

Make sure to adjust these settings for your environment, in particular the `GOROOT` should point to the directory
where you installed Go.

The next time you go into the project directory, the `direnv` tool try to automatically load those settings, but if it
is the first time it will do nothing and ask you to give it permission. You will see an error message like this:

   direnv: error /home/builder/fulfillment-api/.envrc is blocked. Run `direnv allow` to approve its content

Run that `direnv allow` command:

    $ cd ~/fulfillment-api
    direnv: error /home/builder/fulfillment-api/.envrc is blocked. Run `direnv allow` to approve its content

    $ direnv allow
    direnv: loading ~/fulfillment-api/.envrc
    direnv: export +GOBIN +GOPATH +GOROOT +PGDATABASE +PGHOST +PGPASSFILE +PGUSER +VIRTUAL_ENV ~PATH

Any time you enter that directory now you will have the right environment variables, and when you leave the directory it
will clean them up.

In addition, the first time it will automatically create a new Python virtual environment inside the `.venv` directory,
and will activate it when you enter the directory.

Verify that the Python and Go versions are set correctly:

    $ python --version
    Python 3.12.5

    $ go version
    go version go1.22.9 linux/amd64

### Clone the git repository

Clone the git repository into the `repository` sub-directory:

    $ cd ~/fulfillment-api
    $ git clone git@github.com:innabox/fulfillment-api.git repository

### Install the Python packages required by the `dev.py` tool

The `dev.py` tool requires some Python packages that are listed in the `requirements.txt` file, so install them:

    $ cd ~/fulfillment-api/repository
    $ pip install -r requirements.txt

### Use the `dev.py setup` command to install the rest of the development tools

For different development tasks the following tools are used, for example:

- [`buf`](https://buf.build) - Used go check the gRPC specification.
- [`protoc-gen-openapi`](https://github.com/grpc-ecosystem/grpc-gateway) - Used generate the OpenAPI specification.

The recommended way to install them is to use the `dev.py setup` command, which will download and install the right
versions to the `~/fulfillment-api/.local` directory:

    $ cd ~/fulfillment-api/repository
    $ ./dev.py setup

## Development

To check the API specification locally use `./dev.py lint`.

To update the generated OpenAPI specifications use `./dev.py generate`.
