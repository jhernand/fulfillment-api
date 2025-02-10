# Fulfillment API

This project contains the definition of the fulfillment API.

The API is specified using [Protocol Buffers](https://protobuf.dev) and [gRPC](https://grpc.io) definitions inside the
[`proto`](proto/fulfillment/v1) directory. For example, the defintion for the `ClusterOrder` object that will be used to
request the provisioning of a cluster is inside the
[`cluster_order_type.proto`](proto/fulfillment/v1/cluster_order_type.proto) file, and the definition of the operations to
list, get, place and cancel an order are in the
[`cluster_orders_service.proto`](proto/fulfillment/v1/cluster_orders_service.proto) file.

The server will be implemented using Protocol Buffers and gRPC as well, and it will also support plain HTTP and JSON
access via the [gRPC-Gateway](https://grpc-ecosystem.github.io/grpc-gateway).