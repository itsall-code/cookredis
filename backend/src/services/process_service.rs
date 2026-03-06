use anyhow::Context;
use regex::Regex;
use serde_json::Value;

use crate::{
    models::request::{BatchLocalizeRequest, LocalizeAccountRequest},
    services::redis_service,
    utils::msgpack,
};

pub async fn localize_single_account(req: &LocalizeAccountRequest) -> anyhow::Result<String> {
    let source_field = &req.source_field;
    let target_field = req
        .target_field
        .clone()
        .unwrap_or_else(|| format!("{}{}", req.server.pre_login, source_field));

    let raw = redis_service::get_hash_field_bytes(&req.source, &req.hash_name, source_field)
        .await
        .with_context(|| {
            format!(
                "failed to read source hash field: hash={}, field={}",
                req.hash_name, source_field
            )
        })?;

    let mut value = msgpack::decode_to_json_value(&raw)?;
    transform_value_recursive(
        &mut value,
        &req.server.platform,
        &req.server.group,
        &req.server.server,
    )?;

    let encoded = msgpack::encode_from_json_value(&value)?;
    redis_service::set_hash_field_bytes(&req.target, &req.hash_name, &target_field, encoded)
        .await
        .with_context(|| {
            format!(
                "failed to write target hash field: hash={}, field={}",
                req.hash_name, target_field
            )
        })?;

    Ok(target_field)
}

pub async fn localize_batch(req: &BatchLocalizeRequest) -> anyhow::Result<Vec<String>> {
    let mut targets = Vec::with_capacity(req.source_fields.len());

    for field in &req.source_fields {
        let single = LocalizeAccountRequest {
            source: req.source.clone(),
            target: req.target.clone(),
            hash_name: req.hash_name.clone(),
            source_field: field.clone(),
            target_field: Some(format!("{}{}", req.server.pre_login, field)),
            server: req.server.clone(),
        };

        let target = localize_single_account(&single).await?;
        targets.push(target);
    }

    Ok(targets)
}

fn transform_value_recursive(
    value: &mut Value,
    platform: &str,
    group: &str,
    server: &str,
) -> anyhow::Result<()> {
    let server_re = Regex::new(r"S\d+\.")?;

    match value {
        Value::String(s) => {
            let mut out = s.clone();
            out = replace_platform_like(&out, platform);
            out = replace_group_like(&out, group);
            out = server_re.replace_all(&out, format!("{}.", server)).to_string();
            *s = out;
        }
        Value::Array(arr) => {
            for item in arr {
                transform_value_recursive(item, platform, group, server)?;
            }
        }
        Value::Object(map) => {
            for (_, v) in map.iter_mut() {
                transform_value_recursive(v, platform, group, server)?;
            }
        }
        _ => {}
    }

    Ok(())
}

fn replace_platform_like(input: &str, platform: &str) -> String {
    let patterns = [
        r#"\"platform\":\"[^\"]+\""#,
        r#"\"plat\":\"[^\"]+\""#,
        r#"platform=[^,}\]]+"#,
        r#"plat=[^,}\]]+"#,
    ];

    let mut output = input.to_string();
    for p in patterns {
        let re = Regex::new(p).unwrap();
        output = re
            .replace_all(&output, |caps: &regex::Captures| {
                let text = caps.get(0).map(|m| m.as_str()).unwrap_or_default();
                if text.starts_with("\"platform\"") {
                    format!("\"platform\":\"{}\"", platform)
                } else if text.starts_with("\"plat\"") {
                    format!("\"plat\":\"{}\"", platform)
                } else if text.starts_with("platform=") {
                    format!("platform={}", platform)
                } else if text.starts_with("plat=") {
                    format!("plat={}", platform)
                } else {
                    text.to_string()
                }
            })
            .to_string();
    }

    output
}

fn replace_group_like(input: &str, group: &str) -> String {
    let patterns = [
        r#"\"group\":\"[^\"]+\""#,
        r#"\"groupId\":\"[^\"]+\""#,
        r#"group=[^,}\]]+"#,
        r#"groupId=[^,}\]]+"#,
    ];

    let mut output = input.to_string();
    for p in patterns {
        let re = Regex::new(p).unwrap();
        output = re
            .replace_all(&output, |caps: &regex::Captures| {
                let text = caps.get(0).map(|m| m.as_str()).unwrap_or_default();
                if text.starts_with("\"group\"") {
                    format!("\"group\":\"{}\"", group)
                } else if text.starts_with("\"groupId\"") {
                    format!("\"groupId\":\"{}\"", group)
                } else if text.starts_with("group=") {
                    format!("group={}", group)
                } else if text.starts_with("groupId=") {
                    format!("groupId={}", group)
                } else {
                    text.to_string()
                }
            })
            .to_string();
    }

    output
}

