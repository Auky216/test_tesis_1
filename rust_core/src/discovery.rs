use mdns_sd::{ServiceDaemon, ServiceInfo};
use std::collections::HashMap;

pub async fn register_service() {
    let mdns = ServiceDaemon::new().expect("Fallo inicializando mDNS");
    let service_type = "_iot-edge._tcp.local.";
    let instance_name = "rpi5-sensor-hub";
    let ip = "127.0.0.1"; // Se actualizaría dinámicamente según interfaz de red
    let port = 8080; // Puerto del dashboard Axum
    
    let mut properties = HashMap::new();
    properties.insert("sensors".to_string(), "DHT22,HC-SR501,MQ-135".to_string());
    properties.insert("role".to_string(), "hardware_layer".to_string());

    let service = ServiceInfo::new(
        service_type, instance_name, "rpi5.local.", ip, port, properties
    ).unwrap();

    mdns.register(service).expect("Error registrando servicio");
    println!("Autodescubrimiento mDNS activo. Nodo registrado como {}", instance_name);
}
