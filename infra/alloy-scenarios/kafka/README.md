# Kafka Scenarios

Learn how to use Grafana Alloy to monitor logs from Kafka.

## Overview

This demo showcases how to:
- Collect logs from a Kafka topic
- Process and transform JSON log data with Alloy
- Forward processed logs to Loki
- Visualize the logs in Grafana

## Components

- **Kafka**: Message broker storing logs
- **Kafka Producer**: Generates sample logs and sends them to Kafka
- **Grafana Alloy**: Observability pipeline that processes logs
- **Loki**: Log aggregation system
- **Grafana**: Visualization platform

## Running the Demo

### Step 1: Clone the repository
```bash
git clone https://github.com/grafana/alloy-scenarios.git
```

### Step 2: Deploy the monitoring stack
```bash
cd alloy-scenarios/kafka
docker-compose up -d
```

### Step 3: Access Grafana Alloy UI
Open your browser and go to `http://localhost:12345`. 

### Step 4: Access Grafana UI
Open your browser and go to `http://localhost:3000`.

Click `drilldown` to see the logs in Grafana.

## How It Works

1. The `gen_log.sh` script generates random JSON logs with different log levels, applications, and messages
2. These logs are sent to the Kafka topic `alloy-logs`
3. Alloy reads from this Kafka topic, processes the JSON data, and forwards it to Loki
4. Grafana connects to Loki to display and query the processed logs

Try creating dashboards in Grafana to visualize log frequencies by application or error levels!


