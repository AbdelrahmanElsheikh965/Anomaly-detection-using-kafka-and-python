# Efficient Data Stream Anomaly Detection


## The Approach

Firstly, we create a Kafka producer, and then, we generate some data with some noise randomly to be sent with that producer on a certain topic (raw-data) so that it can be consumed by a Kafka consumer then we collect data that the consumer got and try to detect any anomalies within using Isolation-Forest Algorithm finally we visualize everything (normal data as blue line and any anomalies as red dots) found in the real-time like illustrated in the gif below.

![](https://github.com/AbdelrahmanElsheikh965/Research-Project/blob/develop/anomalies.gif)


## Why Isolation Alogirhtm

The Isolation Forest algorithm is an **anomaly detection algorithm** specifically designed to identify rare or anomalous data points within a dataset. Here's a concise explanation of how it works and why it is effective:

### How Isolation Forest Works:

1. **Random Partitioning**: The algorithm builds multiple binary trees by randomly selecting a feature and splitting it at a random threshold. The idea is that anomalies (outliers) are data points that are more isolated from the majority of the data. These points will likely require fewer splits to be isolated.

2. **Isolation Depth**: Points that are anomalies are isolated quickly because they are far from other points. In contrast, normal points are harder to isolate and require more splits. The number of splits required to isolate a point gives a measure of its "anomalousness."

3. **Averaging Across Trees**: The algorithm builds multiple trees (called an "ensemble"), and the average number of splits required to isolate a point across all trees is used to compute an anomaly score. Points with lower scores are more likely to be anomalies.

### Why Isolation Forest is Effective:

- **Efficient for High-dimensional Data**: Unlike other anomaly detection methods (e.g., clustering or density-based methods), Isolation Forest doesn't rely on distance measures, which can become inefficient as dimensionality increases. It works well with high-dimensional data and scales efficiently to large datasets.
  
- **Fast and Scalable**: Its tree-based structure makes the algorithm computationally efficient, particularly for large datasets. It can be used in real-time scenarios because it has a relatively low computational cost.

- **Unsupervised**: The algorithm doesn't require labeled data for training. This makes it useful in situations where you have lots of data but no clear labels for normal vs. anomalous points.

- **Robust to Noise**: The randomness in the way the trees are built ensures that the algorithm is robust to noisy data, making it effective in identifying truly anomalous points even in the presence of noise.

### Effectiveness in Real-time Data:
For real-time streaming data, such as the one you're visualizing in Kafka, Isolation Forest is particularly effective because it can be applied incrementally. It quickly isolates anomalies as new data is received, allowing real-time detection. The algorithm's ability to handle high-dimensional data and scale efficiently makes it ideal for streaming contexts where data is continuously produced and needs to be analyzed on-the-fly.

## Installation

1. Create a Virtual Environment in your project directory:

```
python -m venv venv
```

2. Activate the Virtual Environment:
```
source venv/bin/activate
```

3. Run all deps

```
pip install -r requirements.txt
```

> To list all deps installed Run: pip freeze > requirements.txt
