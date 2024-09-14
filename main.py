from kafka.producer import KafkaProducer # type: ignore
from kafka.consumer import KafkaConsumer # type: ignore
import numpy as np # type: ignore
import json
from sklearn.ensemble import IsolationForest # type: ignore
import matplotlib.pyplot as plt # type: ignore
from matplotlib.animation import FuncAnimation # type: ignore

def create_kafka_producer(bootstrap_servers):
    print("Creating Kafka producer...")
    return KafkaProducer(bootstrap_servers=bootstrap_servers)

def produce_synthetic_data(producer, topic_name, num_data_points=1000):
    print("Producing synthetic data...")
    for i in range(num_data_points):
        value = np.sin(i * 0.1)
        
        if np.random.rand() < 0.01:
            value += np.random.rand() * 5

        data = {
            "value": value,
            "time_step": i
        }
        producer.send(topic_name, value=json.dumps(data).encode("utf-8"))

    producer.flush()
    print("Data production complete.")

def create_kafka_consumer(topic_name, bootstrap_servers):
    print("Creating Kafka consumer...")
    # return KafkaConsumer(topic_name, bootstrap_servers=bootstrap_servers)
    return KafkaConsumer(
        topic_name,
        bootstrap_servers=bootstrap_servers,
        max_poll_records=100,  # Adjust as needed
        fetch_max_bytes=1048576,  # Adjust as needed (1 MB)
        fetch_max_wait_ms=500,  # Adjust as needed (500 ms)
        auto_offset_reset='earliest',
        enable_auto_commit=True
    )


def collect_raw_data(consumer, max_data_points=10):
    print("Collecting raw data...")
    data, time_steps = [], []
    
    for i, msg in enumerate(consumer):
        value = json.loads(msg.value.decode('utf-8'))['value']
        print(f"Value => {value}")
        data.append([value])
        time_steps.append(i)
        print(f"I => {i}")

        if len(data) >= max_data_points:
            break
    
    print(f"Collected {len(data)} data points.")
    return np.array(data), time_steps

def detect_anomalies(X, contamination=0.01):
    print("Detecting anomalies...")
    model = IsolationForest(contamination=contamination)
    model.fit(X)
    pred = model.predict(X)
    anomalies = X[pred == -1]
    anomaly_indices = [i for i, p in enumerate(pred) if p == -1]
    print(f"Detected {len(anomalies)} anomalies.")
    return anomalies, anomaly_indices

def produce_anomalies(producer, topic_name, anomalies, anomaly_time_steps):
    print("Producing anomalies...")
    for anomaly, time_step in zip(anomalies, anomaly_time_steps):
        anomaly_data = {
            "anomalous_value": anomaly[0],
            "time_step": time_step
        }
        # Send serialized data as bytes
        producer.send(topic_name, value=json.dumps(anomaly_data).encode("utf-8"))

    producer.flush()
    print("Anomaly production complete.")


def update_plot(frame, X, anomalies, anomaly_time_steps, line, scatter):
    print("Updating plot...")
    # Set normal data
    line.set_data(range(len(X)), X[:, 0])

    # Ensure the anomalies and their time steps are in the correct format
    if len(anomalies) > 0:
        scatter.set_offsets(np.c_[[time_steps[i] for i in anomaly_time_steps], anomalies])
    else:
        scatter.set_offsets([])  # If no anomalies, clear the scatter plot

    return line, scatter


def data_generator(X, anomalies, anomaly_time_steps):
    while True:
        yield (X, anomalies, anomaly_time_steps)

if __name__ == "__main__":
    bootstrap_servers = 'localhost:9093'

    # Produce synthetic data
    raw_data_producer = create_kafka_producer(bootstrap_servers)
    produce_synthetic_data(raw_data_producer, 'raw-data')
    raw_data_producer.close()

    # Consume raw data
    raw_data_consumer = create_kafka_consumer('raw-data', bootstrap_servers)
    X, time_steps = collect_raw_data(raw_data_consumer)

    # Detect anomalies
    anomalies, anomaly_time_steps = detect_anomalies(X)

    # Produce anomalies
    anomalies_producer = create_kafka_producer(bootstrap_servers)
    produce_anomalies(anomalies_producer, 'anomalies', anomalies, anomaly_time_steps)
    anomalies_producer.close()

    # Print results
    print("Detected anomalies:")
    for anomaly, time_step in zip(anomalies, anomaly_time_steps):
        print(f"Value: {anomaly[0]}, Time-step: {time_step}")

    # Set up real-time visualization
    fig, ax = plt.subplots()
    ax.set_xlim(0, len(X))
    ax.set_ylim(np.min(X) - 1, np.max(X) + 1)
    line, = ax.plot([], [], lw=2, label='Normal Data')
    scatter = ax.scatter([], [], color='red', label='Anomalies')

    ax.legend()

    def init():
        print("Initializing plot...")
        line.set_data([], [])
        scatter.set_offsets([])
        return line, scatter

    ani = FuncAnimation(
        fig, 
        update_plot, 
        frames=data_generator(X, anomalies, anomaly_time_steps),
        init_func=init,
        interval=1000,
        blit=True,
        cache_frame_data=False  # Suppresses the warning
    )


    print("Displaying plot...")
    plt.show()
