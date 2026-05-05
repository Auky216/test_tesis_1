use rumqttc::{AsyncClient, QoS};
use tokio::time::{sleep, Duration};

pub async fn publish_telemetry(client: AsyncClient) {
    loop {
        // Mock de lectura desde sensors.rs
        let payload = r#"{"dht22": {"t": 22.4, "h": 55}, "pir": true, "mq135": 400}"#;
        
        let result = client.publish("iot/telemetry/sensors", QoS::AtLeastOnce, false, payload.as_bytes())
            .await;
            
        if let Err(e) = result {
            eprintln!("Error publicando telemetría: {:?}", e);
        }
            
        sleep(Duration::from_secs(1)).await; // Alta frecuencia determinista
    }
}
