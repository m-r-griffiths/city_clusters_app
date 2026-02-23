import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Page Config - Clean and Light
st.set_page_config(page_title="City Analytics Pro", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    stSelectbox { color: #2c3e50; }
    </style>
    """, unsafe_allow_index=True)

st.title("🏙️ City Analysis Dashboard")
st.markdown("---")

# 2. Robust Data Loading
@st.cache_data
def load_data():
    tsne_df = pd.read_csv('tsne_data.csv')
    radar_df = pd.read_csv('radar_data.csv', index_col=0)
    
    # CRITICAL FIX: Clean the city names to ensure they match perfectly
    tsne_df['City'] = tsne_df['City'].astype(str).str.strip()
    radar_df.index = radar_df.index.astype(str).str.strip()
    
    return tsne_df, radar_df

try:
    df_tsne, df_radar = load_data()
    df_tsne['Cluster label'] = df_tsne['Cluster label'].astype(str)
    
    col1, col2 = st.columns([3, 2], gap="large")

    with col1:
        st.subheader("t-SNE 3D Cluster Mapping")
        
        # Creating a much cleaner 3D Scatter
        fig_tsne = px.scatter_3d(
            df_tsne, 
            x='tsne_1', y='tsne_2', z='tsne_3',
            color='Cluster label',
            hover_name='City',
            height=800,
            template="plotly_white", # Clean white background
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        
        # REMOVE THE "WHITE LINES": Disable spikes and simplify grid
        fig_tsne.update_layout(
            scene=dict(
                xaxis=dict(showspikes=False, backgroundcolor="white", gridcolor="#e5e5e5"),
                yaxis=dict(showspikes=False, backgroundcolor="white", gridcolor="#e5e5e5"),
                zaxis=dict(showspikes=False, backgroundcolor="white", gridcolor="#e5e5e5"),
            ),
            margin=dict(l=0, r=0, b=0, t=0)
        )
        fig_tsne.update_traces(marker=dict(size=4, opacity=0.7, line=dict(width=0)))
        
        st.plotly_chart(fig_tsne, use_container_width=True)

    with col2:
        st.subheader("Cluster Profile (Average)")
        
        cluster_list = sorted(df_tsne['Cluster label'].unique())
        selected_cluster = st.selectbox("Select a Cluster to view details:", options=cluster_list)
        
        # Logic to get cluster average
        cities_in_cluster = df_tsne[df_tsne['Cluster label'] == selected_cluster]['City']
        
        # Filter radar data to only these cities
        # We use .reindex to ensure we only pull rows that actually exist
        cluster_data = df_radar.loc[df_radar.index.intersection(cities_in_cluster)]
        
        if not cluster_data.empty:
            avg_stats = cluster_data.mean()
            
            # Create a professional Radar Chart
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=avg_stats.values,
                theta=avg_stats.index,
                fill='toself',
                fillcolor='rgba(31, 119, 180, 0.4)',
                line=dict(color='#1f77b4', width=2),
                name=f"Cluster {selected_cluster}"
            ))
            
            fig_radar.update_layout(
                polar=dict(
                    bgcolor="white",
                    radialaxis=dict(visible=True, range=[0, df_radar.values.max()], gridcolor="#e5e5e5"),
                    angularaxis=dict(gridcolor="#e5e5e5")
                ),
                showlegend=False,
                template="plotly_white",
                height=500
            )
            st.plotly_chart(fig_radar, use_container_width=True)
            
            # Additional Info
            st.info(f"Showing average for **{len(cluster_data)} cities** in Cluster {selected_cluster}.")
            with st.expander("Show City List"):
                st.write(", ".join(cluster_data.index.tolist()))
        else:
            st.warning("No matching radar data found for the cities in this cluster.")
            # Debug info (hidden by default)
            with st.expander("Debug: Check Data Names"):
                st.write("Cities in t-SNE:", cities_in_cluster.tolist()[:5])
                st.write("Cities in Radar Index:", df_radar.index.tolist()[:5])

except Exception as e:
    st.error(f"Something went wrong: {e}")
