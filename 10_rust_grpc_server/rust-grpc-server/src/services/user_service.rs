use crate::tonic_build_gen::user::v1::{user_service_server::UserService, CreateRequest};

pub struct UserServiceImpl {}

#[tonic::async_trait]
impl UserService for UserServiceImpl {
    async fn create(
        &self,
        _request: tonic::Request<CreateRequest>,
    ) -> std::result::Result<tonic::Response<()>, tonic::Status> {
        // Implement the logic for creating a user here
        Ok(tonic::Response::new(()))
    }
}
