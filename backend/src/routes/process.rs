use axum::{routing::post, Json, Router};

use crate::{
    error::AppError,
    models::{
        request::{BatchLocalizeRequest, LocalizeAccountRequest},
        response::ApiResponse,
    },
    services::process_service,
};

pub fn routes() -> Router {
    Router::new()
        .route("/api/process/localize-account", post(localize_account))
        .route("/api/process/localize-batch", post(localize_batch))
}

async fn localize_account(
    Json(req): Json<LocalizeAccountRequest>,
) -> Result<Json<ApiResponse<String>>, AppError> {
    let target = process_service::localize_single_account(&req).await?;
    Ok(Json(ApiResponse::ok_with_message(
        target,
        "Localized single account successfully".to_string(),
    )))
}

async fn localize_batch(
    Json(req): Json<BatchLocalizeRequest>,
) -> Result<Json<ApiResponse<Vec<String>>>, AppError> {
    let targets = process_service::localize_batch(&req).await?;
    Ok(Json(ApiResponse::ok_with_message(
        targets.clone(),
        format!("Localized {} accounts", targets.len()),
    )))
}
