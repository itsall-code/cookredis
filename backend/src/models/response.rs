use serde::Serialize;

#[derive(Debug, Serialize)]
pub struct ApiResponse<T> {
    pub success: bool,
    pub data: Option<T>,
    pub message: String,
}

impl<T> ApiResponse<T> {
    pub fn ok(data: T) -> Self {
        Self {
            success: true,
            data: Some(data),
            message: "ok".to_string(),
        }
    }

    pub fn ok_with_message(data: T, message: String) -> Self {
        Self {
            success: true,
            data: Some(data),
            message,
        }
    }
}
