import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Page Config
st.set_page_config(page_title="City Cluster Dashboard", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .stSelectbox label { font-weight: bold; color: #2c3e50; }
    </style>
    """, unsafe_allow_html=True)

# UPDATED: Clean title without emoji
st.title("City Cluster Dashboard")
st.markdown("---")

# 2. Load Data
@st.cache_data
def load_data():
    tsne_df = pd.read_csv('tsne_data.csv')
    radar_df = pd.read_csv('radar_data.csv', index_col=0)
    
    tsne_df['City'] = tsne_df['City'].astype(str).str.strip()
    return tsne_df, radar_df

try:
    df_tsne, df_radar = load_data()
    
    # Ensure Cluster labels are integers for sorting, then strings for plotting
    df_tsne['Cluster label'] = df_tsne['Cluster label'].astype(int)
    df_tsne = df_tsne.sort_values('Cluster label')
    
    col1, col2 = st.columns([3, 2], gap="large")

    with col1:
        st.subheader("Cluster Mapping (3D)")
        
        # UPDATED: Added 'labels' to rename legend and sorted dataframe for legend order
        fig_tsne = px.scatter_3d(
            df_tsne, 
            x='tsne_1', y='tsne_2', z='tsne_3',
            color=df_tsne['Cluster label'].astype(str),
            hover_name='City',
            height=750,
            template="plotly_white",
            color_discrete_sequence=px.colors.qualitative.Prism,
            labels={'color': 'Cluster'} 
        )
        
        fig_tsne.update_layout(
            scene=dict(
                xaxis=dict(showspikes=False, gridcolor="#eeeeee", showbackground=False),
                yaxis=dict(showspikes=False, gridcolor="#eeeeee", showbackground=False),
                zaxis=dict(showspikes=False, gridcolor="#eeeeee", showbackground=False),
            ),
            margin=dict(l=0, r=0, b=0, t=0),
            legend_title_text='Cluster'
        )
        fig_tsne.update_traces(marker=dict(size=4, opacity=0.8))
        st.plotly_chart(fig_tsne, use_container_width=True)

    with col2:
        # UPDATED: Clean header
        st.subheader("Cluster Profile")
        
        cluster_list = sorted(df_tsne['Cluster label'].unique())
        selected_cluster = st.selectbox("Select a Cluster to analyze:", options=cluster_list)
        
        try:
            cluster_stats = df_radar.loc[selected_cluster]
            
            values = cluster_stats.values.tolist()
            labels = cluster_stats.index.tolist()
            values += values[:1]
            labels += labels[:1]
            
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=values,
                theta=labels,
                fill='toself',
                fillcolor='rgba(0, 104, 201, 0.2)',
                line=dict(color='#0068C9', width=2),
                name=f"Cluster {selected_cluster}"
            ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True, 
                        range=[0, 1],
                        tickvals=[0, 0.5, 1],
                        gridcolor="#eeeeee"
                    ),
                    angularaxis=dict(gridcolor="#eeeeee")
                ),
                showlegend=False,
                template="plotly_white",
                height=500
            )
            st.plotly_chart(fig_radar, use_container_width=True)
            
            cities_in_cluster = df_tsne[df_tsne['Cluster label'] == selected_cluster]['City'].tolist()
            st.success(f"This profile represents the average of **{len(cities_in_cluster)}** cities.")
            with st.expander("Show Cities in this Cluster"):
                st.write(", ".join(sorted(cities_in_cluster)))
                
        except KeyError:
            st.error(f"Cluster {selected_cluster} not found in radar_data.csv")

except Exception as e:
    st.error(f"Error: {e}")
