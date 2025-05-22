use tonic::codegen::http::Request;
use tonic::{async_trait, body::BoxBody, Status};
use tonic_middleware::RequestInterceptor;

#[derive(Clone)]
pub struct SampleInterceptor {}

#[async_trait]
impl RequestInterceptor for SampleInterceptor {
    async fn intercept(&self, request: Request<BoxBody>) -> Result<Request<BoxBody>, Status> {
        // Example: Add custom logic here if needed
        println!("Intercepted request: {:?}", request);
        Ok(request)
    }
}
