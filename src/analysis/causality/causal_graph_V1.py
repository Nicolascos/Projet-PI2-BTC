import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from sklearn.covariance import GraphicalLassoCV
from sklearn.preprocessing import StandardScaler

# 1. Load Data
try:
    df = pd.read_csv('../../../data/processed/Three_Pillars_Dataset.csv', index_col=0, parse_dates=True)
    
    # 2. Select Key Nodes (Representatives from MDA Clusters)
    # Target: Bitcoin Price
    # Cluster 3 (The Big One): HashRate (Network), total_stablecoin_mcap (Liquidity), BlackRock Bitcoin (Inst. Sentiment)
    # Cluster 18/20 (Macro): CESIJPY (Macro Surprise)
    # Cluster 6 (Retail): Coinbase (Retail Sentiment)
    # Cluster 8 (Activity): AdrActCnt (Usage)
    # Fundamental Context: CapMVRVCur (Valuation)
    
    nodes = [
        'XBTUSD', 
        'HashRate', 
        'total_stablecoin_mcap', 
        'BlackRock Bitcoin', 
        'CESIJPY', 
        'Coinbase', 
        'AdrActCnt', 
        'CapMVRVCur'
    ]
    
    data = df[nodes].copy()
    
    # 3. Stationarity Transformations (Crucial for Causal Analysis)
    # Most financial time series are random walks; we need changes (returns/diffs).
    
    # Log Returns for prices and exponential metrics
    for col in ['XBTUSD', 'HashRate', 'total_stablecoin_mcap', 'AdrActCnt']:
        data[col] = np.log(data[col]).diff()
        
    # Simple Differencing for bounded/ratio metrics
    for col in ['BlackRock Bitcoin', 'CESIJPY', 'Coinbase', 'CapMVRVCur']:
        data[col] = data[col].diff()
        
    # Drop the first NaN row created by differencing
    data = data.dropna()
    
    # 4. Estimate Causal Skeleton (Partial Correlation via Graphical Lasso)
    # Partial Correlation removes indirect effects (e.g., if A->B->C, PartCorr(A,C) ~ 0)
    
    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(data)
    
    # Graphical Lasso estimates the precision matrix (inverse covariance)
    # The non-zero elements of the precision matrix correspond to the edges of the graph
    model = GraphicalLassoCV(cv=5)
    model.fit(data_scaled)
    precision_matrix = model.precision_
    
    # Convert Precision Matrix to Partial Correlation Matrix
    # rho_ij = -p_ij / sqrt(p_ii * p_jj)
    n_features = precision_matrix.shape[0]
    partial_corr = np.zeros((n_features, n_features))
    
    for i in range(n_features):
        for j in range(n_features):
            if i == j:
                partial_corr[i, j] = 1.0
            else:
                partial_corr[i, j] = -precision_matrix[i, j] / np.sqrt(precision_matrix[i, i] * precision_matrix[j, j])
                
    partial_corr_df = pd.DataFrame(partial_corr, index=nodes, columns=nodes)
    
    # 5. Visualize the Graph
    plt.figure(figsize=(12, 10))
    
    # Create Graph from Partial Correlation Matrix
    G = nx.Graph()
    
    # Add nodes
    for node in nodes:
        G.add_node(node)
        
    # Add edges for strong partial correlations
    threshold = 0.05 # Threshold to filter noise
    edges = []
    weights = []
    
    for i in range(n_features):
        for j in range(i + 1, n_features):
            weight = partial_corr[i, j]
            if abs(weight) > threshold:
                G.add_edge(nodes[i], nodes[j], weight=weight)
                edges.append((nodes[i], nodes[j]))
                weights.append(weight)

    # Layout
    pos = nx.spring_layout(G, k=0.5, seed=42)
    
    # Draw Nodes
    nx.draw_networkx_nodes(G, pos, node_size=3000, node_color='lightblue', edgecolors='black')
    
    # Draw Labels
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
    
    # Draw Edges (Thickness = Strength, Color = Sign)
    positive_edges = [(u, v) for (u, v, d) in G.edges(data=True) if d['weight'] > 0]
    negative_edges = [(u, v) for (u, v, d) in G.edges(data=True) if d['weight'] < 0]
    
    # Widths
    pos_widths = [G[u][v]['weight'] * 10 for u, v in positive_edges]
    neg_widths = [abs(G[u][v]['weight']) * 10 for u, v in negative_edges]
    
    nx.draw_networkx_edges(G, pos, edgelist=positive_edges, width=pos_widths, edge_color='green', alpha=0.6)
    nx.draw_networkx_edges(G, pos, edgelist=negative_edges, width=neg_widths, edge_color='red', alpha=0.6)
    
    plt.title("Learned Causal Skeleton (Partial Correlation Graph)\nGreen=Positive Link, Red=Negative Link", fontsize=15)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('../../../data/outputs/images/causal_skeleton.png')
    
    # Save the partial correlation matrix
    partial_corr_df.to_csv('../../../data/outputs/metrics/partial_correlation_matrix.csv')
    
    print("Graph generation complete.")
    print("Nodes selected:", nodes)
    
except Exception as e:
    print(f"Error: {e}")