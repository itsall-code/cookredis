use std::{fs, path::Path};

use anyhow::Context;

use crate::models::config::AppConfig;

pub fn load_app_config<P: AsRef<Path>>(path: P) -> anyhow::Result<AppConfig> {
    let path_ref = path.as_ref();
    let text = fs::read_to_string(path_ref)
        .with_context(|| format!("failed to read config: {}", path_ref.display()))?;
    let cfg: AppConfig = serde_json::from_str(&text)
        .with_context(|| format!("failed to parse config: {}", path_ref.display()))?;
    Ok(cfg)
}
