import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Page Configuration
st.set_page_config(page_title="City Clustering Dashboard", layout="wide")

st.title("🏙️ City Analysis: t-SNE Clusters & Radar Profiles")
st.markdown("Explore the 3D t-SNE clusters on the left and see the average profile for each cluster on the right.")

# 2. Load Data
@st.cache_data
def load_data():
    tsne_df = pd.read_csv('tsne_data.csv')
    radar_df = pd.read_csv('radar_data.csv', index_col=0)
    return tsne_df, radar_df

try:
    df_tsne, df_radar = load_data()
    
    # Ensure Cluster label is a string for discrete coloring
    df_tsne['Cluster label'] = df_tsne['Cluster label'].astype(str)
    
    # 3. Create Layout Columns
    col1, col2 = st.columns([3, 2])

    with col1:
        st.subheader("3D t-SNE Projection")
        fig_tsne = px.scatter_3d(
            df_tsne, 
            x='tsne_1', y='tsne_2', z='tsne_3',
            color='Cluster label',
            hover_name='City',
            height=700,
            template="plotly_dark"
        )
        fig_tsne.update_traces(marker=dict(size=5, opacity=0.8))
        st.plotly_chart(fig_tsne, use_container_width=True)

    with col2:
        st.subheader("Cluster Personality Profile")
        
        # 1. User picks the Cluster
        cluster_options = sorted(df_tsne['Cluster label'].unique())
        selected_cluster = st.selectbox("Select a Cluster to analyze:", options=cluster_options)
        
        # 2. Identify cities in this cluster
        cities_in_cluster = df_tsne[df_tsne['Cluster label'] == selected_cluster]['City']
        
        # 3. Calculate average stats for the radar
        # We ensure we only use cities that exist in both dataframes
        valid_cities = [c for c in cities_in_cluster if c in df_radar.index]
        cluster_stats = df_radar.loc[valid_cities].mean()
        
        # 4. Create the Radar Chart
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=cluster_stats.values,
            theta=cluster_stats.index,
            fill='toself',
            name=f"Cluster {selected_cluster} Avg",
            line_color='#FFA15A' 
        ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, df_radar.values.max()])
            ),
            showlegend=True,
            template="plotly_dark"
        )
        st.plotly_chart(fig_radar, use_container_width=True)

        # 5. Expandable list of cities
        with st.expander(f"See all {len(valid_cities)} cities in Cluster {selected_cluster}"):
            st.write(", ".join(sorted(valid_cities)))
            
except Exception as e:
    st.error(f"Error: {e}")
    st.info("Check that your CSV files are uploaded correctly to GitHub.")
