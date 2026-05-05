use tokio;
use rumqttc::{AsyncClient, MqttOptions};
use std::time::Duration;

mod discovery;
mod mqtt;
// mod sensors;
// mod dashboard;

#[tokio::main]
async fn main() {
    println!("Iniciando Nodo IoT Hardware (Rust)...");

    // 1. Iniciar Autodescubrimiento mDNS
    tokio::spawn(async {
        discovery::register_service().await;
    });

    // 2. Conectar a MQTT local
    let mut mqttoptions = MqttOptions::new("rust_sensor_agent", "127.0.0.1", 1883);
    mqttoptions.set_keep_alive(Duration::from_secs(5));
    let (client, mut eventloop) = AsyncClient::new(mqttoptions, 10);

    // Tarea: Publicar telemetría constante (no bloqueante)
    let client_clone = client.clone();
    tokio::spawn(async move {
        mqtt::publish_telemetry(client_clone).await;
    });

    // 3. Mantener bucle de eventos MQTT y reconexiones
    loop {
        if let Ok(event) = eventloop.poll().await {
            // Manejar respuestas o configuraciones entrantes
            // println!("MQTT Event: {:?}", event);
            let _ = event; // Ignorar warning de unused temporalmente
        }
    }
}
