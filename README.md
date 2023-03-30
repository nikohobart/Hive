# Hive
A distributed computing framework loosely based on Ray and Dask.

## Structure

|Package|Description|
|:--:|:--|
|`util`|GRPC Utils|
|`models`|Model Definitions|
|`proto`|Generated Protobuf files|
|`services`|Implementation of the Protobuf API|
|`store`|Global Service Store|

## Set Up
We recommend using a virtual environment to manage dependencies.

> to install requirements

```shell
pip install -r requirements.txt
```

> to add to the dependencies list

```shell
pip freeze > requirements.txt
```

The process for editing `.proto` files is outlined below.

> to generate the file's corresponding rpc stubs

```shell
python -m grpc_tools.protoc -I ./protobuf --python_out=./src/proto --grpc_python_out=./src/proto ./protobuf/{file_name}
```

**Importantly**, because I don't understand Python import rules and didn't want to spend anymore time trying to figure out a better solution, after generating a new rpc stub, **you must** change the import line in the generated `_grpc.py` file from `import {.proto_name}_pb2 as {.proto_name}__pb2` to `from src.proto import {.proto_name}_pb2 as {.proto_name}__pb2`.

## General Information
Hive uses `gRPC` and `cloudpickle` for rpc calls and serialization/deserialization, respectively.

The repo follows the general template outlined at this link: [Example Repo](https://github.com/chryb/python-grpc-server-template)

See [here](https://grpc.io/docs/languages/python/quickstart/) for a walkthrough on how to get started with gRPC.

Run `client.py` or `server.py` in the `src` directory to start program. Alternatively, if you want to experiment with the Hive api, use `example.py`.

You can also run servers locally with Docker. Follow the steps outlined below to do so:

> to build the image

```shell
docker build --tag hive-server
```

> to build and run a container with a hive server running on port

```shell
docker run -it -p {port}:{port} -e PYTHONPATH=. hive-server python3 ./src/server.py -p {port}
```

## Troubleshooting
The following are same issues you may run into, if, like me, you haven't done a project in Python for 3 years!
* If you're using VS Code and virtualenv to manage your Python environment, you may have to follow the instructions [here](https://stackoverflow.com/questions/56199111/visual-studio-code-cmd-error-cannot-be-loaded-because-running-scripts-is-disabl/67420296#67420296) to enable the execution of venv activate.
* Make sure to include the Hive directory on your PYTHONPATH so that you don't have to deal with a `ModuleNotFoundError` for an annoying duration of time.

Here are some issues that might pop up in the future to be on the lookout for:
* Cloudpickle only has compatible serializations across the same Python version. Which I think only means every server instance will need to be running the same Python version.
