use opentelemetry_datadog::{new_pipeline, ApiVersion};
use std::error::Error;
use std::str::FromStr;
use tracing::Level;
use tracing::Subscriber;
use tracing_subscriber::layer::SubscriberExt;
use tracing_subscriber::Registry;
use tracing_subscriber::{filter, prelude::*};

pub fn datadog_subscriber() -> Result<(), Box<dyn Error>> {
    let tracer = new_pipeline()
        .with_service_name("{service_name}") // TODO: サービス名設定
        .with_api_version(ApiVersion::Version05)
        .with_agent_endpoint("{endpoint}") // TODO: エンドポイント設定
        .install_batch(opentelemetry_sdk::runtime::Tokio)?;
    let telemetry_layer = tracing_opentelemetry::layer().with_tracer(tracer);

    let stdout_log_layer = tracing_subscriber::fmt::layer()
        .json()
        .with_current_span(true)
        .with_file(true)
        .with_line_number(true)
        .with_thread_ids(true)
        .with_thread_names(true);

    let level = Level::from_str("info")?;
    let level_filter = filter::LevelFilter::from_level(level);

    // ノイズとなるようなトレースを除外するフィルタ
    let common_target_exclusions = filter::filter_fn(|metadata| {
        let target = metadata.target();
        if target.starts_with("hyper") {
            return false;
        }
        true
    });

    let subscriber = Registry::default()
        .with(telemetry_layer.with_filter(common_target_exclusions.clone()))
        .with(
            stdout_log_layer
                .with_filter(level_filter)
                .with_filter(common_target_exclusions),
        );

    init_subscriber(subscriber)
}

fn init_subscriber(
    subscriber: impl Subscriber + Send + Sync + 'static,
) -> Result<(), Box<dyn Error>> {
    tracing::subscriber::set_global_default(subscriber).map_err(|e| e.into())
}
