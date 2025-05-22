use std::net::SocketAddr;

use rust_grpc_server::{
    middleware::sample_interceptor::SampleInterceptor, services::user_service::UserServiceImpl,
    tonic_build_gen::user::v1::user_service_server::UserServiceServer,
};
use tonic::transport::Server;
use tonic_health::{pb::FILE_DESCRIPTOR_SET, server::health_reporter};
use tonic_middleware::RequestInterceptorLayer;
use tonic_reflection::server::Builder;
use tower::ServiceBuilder;

#[tokio::main]
async fn main() {
    let addr: String = "0.0.0.0:50051".parse().unwrap();
    let addr: SocketAddr = addr.parse().expect("failed to parse address");

    // NOTE: 実際に使用する場合は、サービス名やエンドポイントを設定する必要がある
    // datadog_subscriber().expect("failed to initialize datadog subscriber");

    // 本来、本番環境ではリフレクションの登録は行わない
    let refrection = Builder::configure()
        .register_encoded_file_descriptor_set(include_bytes!("tonic_build_gen/descriptor.bin"))
        .register_encoded_file_descriptor_set(FILE_DESCRIPTOR_SET)
        .build_v1()
        .expect("failed to create reflection service");

    let (mut health_reporter, health_service) = health_reporter();
    health_reporter
        .set_serving::<UserServiceServer<UserServiceImpl>>()
        .await;

    let user_service_with_middleware = ServiceBuilder::new()
        .layer(RequestInterceptorLayer::new(SampleInterceptor {}))
        .service(UserServiceServer::new(UserServiceImpl {}));

    Server::builder()
        .add_service(health_service)
        .add_service(refrection)
        .add_service(user_service_with_middleware)
        .serve(addr)
        .await
        .expect("failed to start gRPC server");
}
