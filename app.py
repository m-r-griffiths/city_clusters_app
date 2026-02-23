import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Page Configuration
st.set_page_config(page_title="City Clustering Dashboard", layout="wide")

st.title("🏙️ City Analysis: t-SNE Clusters & Radar Profiles")
st.markdown("Use the 3D plot to explore clusters and select a city to see its specific feature breakdown.")

# 2. Load Data (Using relative paths for GitHub/Streamlit Cloud)
@st.cache_data
def load_data():
    # We use these filenames because they are in the same GitHub folder
    tsne_df = pd.read_csv('tsne_data.csv')
    radar_df = pd.read_csv('radar_data.csv', index_col=0)
    return tsne_df, radar_df

try:
    df_tsne, df_radar = load_data()
    
    # 3. Create Layout Columns
    col1, col2 = st.columns([3, 2])

    with col1:
        st.subheader("3D t-SNE Projection")
        # Ensure Cluster label is a string so the legend is discrete colors
        df_tsne['Cluster label'] = df_tsne['Cluster label'].astype(str)
        
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
        st.subheader("City Radar Profile")
        
        # User selection for the Radar Plot
        selected_city = st.selectbox(
            "Select a city to inspect:", 
            options=sorted(df_tsne['City'].unique())
        )
        
        if selected_city:
            # Get data for selected city
            city_stats = df_radar.loc[selected_city]
            
            # Create the Radar Chart
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=city_stats.values,
                theta=city_stats.index,
                fill='toself',
                name=selected_city,
                line_color='#00CC96'
            ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, df_radar.values.max()])
                ),
                showlegend=True,
                template="plotly_dark"
            )
            st.plotly_chart(fig_radar, use_container_width=True)
            
            # Optional: Show raw data for the selected city
            st.write(f"Raw data for {selected_city}:")
            st.dataframe(city_stats.to_frame().T)

except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("Check that tsne_data.csv and radar_data.csv are in your GitHub repository.")
