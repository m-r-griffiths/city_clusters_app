import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Page Config - FIX: Use correct HTML argument
st.set_page_config(page_title="City Analytics Pro", layout="wide")

# Custom CSS for a cleaner look
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .stSelectbox label { font-weight: bold; color: #2c3e50; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏙️ City Analysis Dashboard")
st.markdown("---")

# 2. Robust Data Loading with strict cleaning
@st.cache_data
def load_data():
    tsne_df = pd.read_csv('tsne_data.csv')
    radar_df = pd.read_csv('radar_data.csv', index_col=0)
    
    # FORCED CLEANING: Remove spaces, force strings, ensure case match
    tsne_df['City'] = tsne_df['City'].astype(str).str.strip()
    radar_df.index = radar_df.index.astype(str).str.strip()
    
    return tsne_df, radar_df

try:
    df_tsne, df_radar = load_data()
    df_tsne['Cluster label'] = df_tsne['Cluster label'].astype(str)
    
    # Sidebar Info
    st.sidebar.header("Data Health Check")
    st.sidebar.write(f"Total Cities in t-SNE: **{len(df_tsne)}**")
    st.sidebar.write(f"Total Cities in Radar Data: **{len(df_radar)}**")

    col1, col2 = st.columns([3, 2], gap="large")

    with col1:
        st.subheader("Cluster Mapping (3D)")
        
        # Clean White 3D Plot
        fig_tsne = px.scatter_3d(
            df_tsne, 
            x='tsne_1', y='tsne_2', z='tsne_3',
            color='Cluster label',
            hover_name='City',
            height=700,
            template="plotly_white",
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        
        # REMOVE CLUTTER: No spikes, clean grid
        fig_tsne.update_layout(
            scene=dict(
                xaxis=dict(showspikes=False, gridcolor="#eeeeee", showbackground=False),
                yaxis=dict(showspikes=False, gridcolor="#eeeeee", showbackground=False),
                zaxis=dict(showspikes=False, gridcolor="#eeeeee", showbackground=False),
            ),
            margin=dict(l=0, r=0, b=0, t=0)
        )
        fig_tsne.update_traces(marker=dict(size=4, opacity=0.8))
        st.plotly_chart(fig_tsne, use_container_width=True)

    with col2:
        st.subheader("Cluster Profile")
        
        cluster_list = sorted(df_tsne['Cluster label'].unique())
        selected_cluster = st.selectbox("Choose a Cluster:", options=cluster_list)
        
        # Match cities between the two files
        cities_in_cluster = df_tsne[df_tsne['Cluster label'] == selected_cluster]['City'].tolist()
        
        # Find the intersection (cities present in both)
        valid_cities = [c for c in cities_in_cluster if c in df_radar.index]
        
        if valid_cities:
            cluster_avg = df_radar.loc[valid_cities].mean()
            
            # Professional Radar
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=cluster_avg.values,
                theta=cluster_avg.index,
                fill='toself',
                fillcolor='rgba(0, 104, 201, 0.2)',
                line=dict(color='#0068C9', width=2),
                name=f"Cluster {selected_cluster}"
            ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, df_radar.values.max()]),
                ),
                showlegend=False,
                template="plotly_white",
                height=450
            )
            st.plotly_chart(fig_radar, use_container_width=True)
            st.success(f"Averaging **{len(valid_cities)}** cities from this cluster.")
        else:
            st.error("No Radar Data Match Found")
            st.write("The names in your Radar CSV don't match the names in your t-SNE CSV.")
            with st.expander("Troubleshoot Names"):
                st.write("Expected Names (from t-SNE):", cities_in_cluster[:5])
                st.write("Available Names (from Radar):", list(df_radar.index)[:5])

except Exception as e:
    st.error(f"Critical Error: {e}")
