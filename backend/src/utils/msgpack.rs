use anyhow::Context;
use serde_json::Value;

pub fn decode_to_json_value(bytes: &[u8]) -> anyhow::Result<Value> {
    let value: Value =
        rmp_serde::from_slice(bytes).context("failed to decode msgpack into json value")?;
    Ok(value)
}

pub fn encode_from_json_value(value: &Value) -> anyhow::Result<Vec<u8>> {
    let bytes = rmp_serde::to_vec_named(value).context("failed to encode json value to msgpack")?;
    Ok(bytes)
}
