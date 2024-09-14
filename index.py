import matplotlib.pyplot as plt # type: ignore
import matplotlib.animation as animation # type: ignore
from kafka.producer import KafkaProducer# type: ignore
from kafka.consumer import KafkaConsumer# type: ignore
import numpy as np# type: ignore
import json
import time
from sklearn.ensemble import IsolationForest# type: ignore


def create_kafka_producer(bootstrap_servers):
    """
    Create and return a Kafka producer.
    """
    print("[DEBUG] Creating Kafka Producer...")
    return KafkaProducer(bootstrap_servers=bootstrap_servers)

def produce_synthetic_data(producer, topic_name, num_data_points=100):
    """
    Produce synthetic data with occasional anomalies and send it to a Kafka topic.
    """
    print(f"[DEBUG] Producing {num_data_points} synthetic data points...")
    for i in range(num_data_points):
        value = np.sin(i * 0.1)
        
        if np.random.rand() < 0.1:  # Increased anomaly chance for faster results
            value += np.random.rand() * 5

        data = {
            "value": value,
            "time_step": i
        }
        print(f"[DEBUG] Produced data: {data}")
        producer.send(topic_name, value=json.dumps(data).encode("utf-8"))
        time.sleep(0.01)  # Small delay to simulate real-time data production

    producer.flush()
    print("[DEBUG] Finished producing data.")

def create_kafka_consumer(topic_name, bootstrap_servers):
    """
    Create and return a Kafka consumer with a timeout.
    """
    print(f"[DEBUG] Creating Kafka Consumer for topic '{topic_name}'...")
    return KafkaConsumer(topic_name, bootstrap_servers=bootstrap_servers, consumer_timeout_ms=10000)  # Timeout after 10s

def collect_raw_data(consumer, max_data_points=100):
    """
    Collect raw data from a Kafka topic.
    """
    print(f"[DEBUG] Collecting raw data (max {max_data_points} points)...")
    data, time_steps = [], []
    
    for i, msg in enumerate(consumer):
        value = json.loads(msg.value.decode('utf-8'))['value']
        data.append([value])
        time_steps.append(i)

        print(f"[DEBUG] Collected data point: {value} at time-step {i}")

        if len(data) >= max_data_points:
            break

    if not data:
        print("[DEBUG] No data received. Exiting collection.")
    else:
        print(f"[DEBUG] Finished collecting {len(data)} raw data points.")
    
    return np.array(data), time_steps

def detect_anomalies(X, contamination=0.1):
    """
    Detect anomalies in the data using the Isolation Forest algorithm.
    """
    print("[DEBUG] Detecting anomalies using Isolation Forest...")
    model = IsolationForest(contamination=contamination)
    model.fit(X)
    pred = model.predict(X)
    anomalies = X[pred == -1]
    anomaly_indices = [i for i, p in enumerate(pred) if p == -1]

    print(f"[DEBUG] Detected {len(anomalies)} anomalies.")
    return anomalies, anomaly_indices

def produce_anomalies(producer, topic_name, anomalies, anomaly_time_steps):
    """
    Send detected anomalies to a Kafka topic.
    """
    print("[DEBUG] Producing detected anomalies...")
    for anomaly, time_step in zip(anomalies, anomaly_time_steps):
        anomaly_data = {
            "anomalous_value": anomaly[0],
            "time_step": time_step
        }
        print(f"[DEBUG] Produced anomaly: {anomaly_data}")
        producer.send(topic_name, value=json.dumps(anomaly_data))

    producer.flush()
    print("[DEBUG] Finished producing anomalies.")

def real_time_visualization(X, time_steps, anomalies, anomaly_time_steps):
    """
    Real-time visualization of data and detected anomalies.
    """
    print("[DEBUG] Starting real-time visualization...")
    fig, ax = plt.subplots()

    def animate(i):
        ax.clear()
        ax.plot(time_steps[:i], X[:i], label='Data Stream', color='blue')
        
        # Mark anomalies in red
        anomaly_steps_so_far = [t for t in anomaly_time_steps if t <= i]
        anomaly_values_so_far = [X[t] for t in anomaly_steps_so_far]
        
        ax.scatter(anomaly_steps_so_far, anomaly_values_so_far, color='red', label='Anomalies')
        ax.legend()

    ani = animation.FuncAnimation(fig, animate, frames=len(time_steps), interval=100)
    plt.show()

if __name__ == "__main__":
    bootstrap_servers = 'localhost:9093'

    # Produce synthetic data
    raw_data_producer = create_kafka_producer(bootstrap_servers)
    produce_synthetic_data(raw_data_producer, 'myFirstTopic', num_data_points=100)  # Reduced data points for faster results
    raw_data_producer.close()

    # Consume raw data
    raw_data_consumer = create_kafka_consumer('myFirstTopic', bootstrap_servers)
    X, time_steps = collect_raw_data(raw_data_consumer, max_data_points=100)  # Reduced max data points for faster results

    if len(X) > 0:
        # Detect anomalies
        anomalies, anomaly_time_steps = detect_anomalies(X)

        # Produce anomalies
        anomalies_producer = create_kafka_producer(bootstrap_servers)
        produce_anomalies(anomalies_producer, 'anomalies', anomalies, anomaly_time_steps)
        anomalies_producer.close()

        # Real-time visualization
        real_time_visualization(X, time_steps, anomalies, anomaly_time_steps)

        # Print results
        print("Detected anomalies:")
        for anomaly, time_step in zip(anomalies, anomaly_time_steps):
            print(f"Value: {anomaly[0]}, Time-step: {time_step}")