import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import os

st.set_page_config(
    page_title="Observatoire Numérique Étudiant",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .main-header { text-align: center; padding: 2rem 0 1rem; }
    .badge {
        background: #1a1a2e; color: #e94560;
        padding: 4px 14px; border-radius: 20px;
        font-size: 13px; font-weight: 700;
        display: inline-block; margin-bottom: 10px;
        border: 1px solid #e94560;
    }
    div[data-testid="metric-container"] {
        background: #1a1a2e; border: 1px solid #e94560;
        border-radius: 10px; padding: 10px;
    }
    div[data-testid="metric-container"] label { color: #a0a0b0 !important; }
    div[data-testid="metric-container"] div { color: #e94560 !important; }
</style>
""", unsafe_allow_html=True)

DATA_FILE = "data_numerique.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            records = json.load(f)
            return pd.DataFrame(records) if records else pd.DataFrame()
    return pd.DataFrame()

def save_data(df):
    with open(DATA_FILE, "w") as f:
        json.dump(df.to_dict(orient="records"), f, ensure_ascii=False)

st.markdown("""
<div class="main-header">
    <span class="badge">📱 INF 232 EC2 — TP Collecte & Analyse</span>
    <h1 style="font-size:2rem; font-weight:700; margin:8px 0 6px; color:#e94560;">
        Observatoire Numérique Étudiant
    </h1>
    <p style="color:#a0a0b0; font-size:15px;">
        Collecte et analyse descriptive des habitudes numériques des étudiants
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()

tab1, tab2, tab3 = st.tabs(["📋 Formulaire", "📊 Dashboard", "🗃️ Données brutes"])

with tab1:
    st.subheader("🖊️ Renseignez vos habitudes numériques")
    st.caption("Données anonymes — utilisées à des fins académiques uniquement.")

    with st.form("form_numerique", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            filiere = st.selectbox("Filière *", ["", "Informatique", "Mathématiques",
                                                  "Physique", "Biologie", "Économie",
                                                  "Droit", "Médecine", "Autre"])
            age = st.number_input("Âge *", min_value=15, max_value=45, value=20)
            smartphone = st.slider("Heures/jour sur smartphone *", 0.0, 16.0, 4.0, 0.5, format="%.1f h")
            reseaux = st.slider("Heures/jour sur réseaux sociaux *", 0.0, 12.0, 2.0, 0.5, format="%.1f h")
            jeux = st.slider("Heures/jour sur jeux vidéo *", 0.0, 10.0, 1.0, 0.5, format="%.1f h")
        with col2:
            niveau = st.selectbox("Niveau *", ["", "L1", "L2", "L3", "M1", "M2", "Doctorat"])
            genre = st.selectbox("Genre *", ["", "Masculin", "Féminin", "Autre"])
            streaming = st.slider("Heures/jour streaming *", 0.0, 10.0, 2.0, 0.5, format="%.1f h")
            travail_pc = st.slider("Heures/jour travail PC *", 0.0, 12.0, 3.0, 0.5, format="%.1f h")
            sommeil = st.slider("Heures de sommeil/nuit *", 3.0, 12.0, 7.0, 0.5, format="%.1f h")

        reseau_prefere = st.selectbox("Réseau social préféré *",
                                      ["", "TikTok", "Instagram", "YouTube", "Facebook",
                                       "WhatsApp", "Twitter/X", "Snapchat", "Autre"])
        telephone_nuit = st.radio("Téléphone au lit avant de dormir ? *",
                                   ["", "Jamais", "Rarement", "Souvent", "Toujours"],
                                   horizontal=True)
        addiction = st.slider("Dépendance perçue au smartphone (1=faible, 10=fort) *", 1, 10, 5)
        impact_etudes = st.selectbox("Impact du numérique sur vos études *",
                                     ["", "Très positif", "Positif", "Neutre", "Négatif", "Très négatif"])
        commentaire = st.text_area("Commentaire (optionnel)", placeholder="Remarques sur vos habitudes numériques...")

        submitted = st.form_submit_button("✅ Soumettre", use_container_width=True)

        if submitted:
            if not all([filiere, niveau, genre, reseau_prefere, telephone_nuit, impact_etudes]):
                st.error("⚠️ Veuillez remplir tous les champs obligatoires (*).")
            else:
                df = load_data()
                new_row = pd.DataFrame([{
                    "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "filiere": filiere, "niveau": niveau, "age": age, "genre": genre,
                    "smartphone_h": smartphone, "reseaux_h": reseaux, "jeux_h": jeux,
                    "streaming_h": streaming, "travail_pc_h": travail_pc, "sommeil_h": sommeil,
                    "reseau_prefere": reseau_prefere, "telephone_nuit": telephone_nuit,
                    "addiction_score": addiction, "impact_etudes": impact_etudes,
                    "commentaire": commentaire
                }])
                df = pd.concat([df, new_row], ignore_index=True)
                save_data(df)
                st.success("🎉 Réponse enregistrée ! Merci pour votre participation.")
                st.balloons()

with tab2:
    df = load_data()
    if df.empty:
        st.info("Aucune donnée encore. Remplissez le formulaire pour voir l'analyse.")
    else:
        for col in ["age", "smartphone_h", "reseaux_h", "jeux_h",
                    "streaming_h", "travail_pc_h", "sommeil_h", "addiction_score"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        n = len(df)
        st.subheader(f"📊 Analyse descriptive — {n} répondant(s)")
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Répondants", n)
        c2.metric("Smartphone/jour", f"{df['smartphone_h'].mean():.1f} h")
        c3.metric("Réseaux/jour", f"{df['reseaux_h'].mean():.1f} h")
        c4.metric("Streaming/jour", f"{df['streaming_h'].mean():.1f} h")
        c5.metric("Score addiction", f"{df['addiction_score'].mean():.1f}/10")

        st.divider()
        COLORS = ["#e94560","#0f3460","#533483","#f5a623","#7ed6df","#e056fd","#badc58","#f9ca24"]

        col_a, col_b = st.columns(2)
        with col_a:
            fig1 = px.bar(df['reseau_prefere'].value_counts().reset_index(),
                          x='reseau_prefere', y='count', title="📱 Réseau social préféré",
                          color='reseau_prefere', color_discrete_sequence=COLORS,
                          labels={'reseau_prefere': 'Réseau', 'count': 'Effectif'})
            fig1.update_layout(showlegend=False, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig1, use_container_width=True)

            fig2 = px.pie(df, names='telephone_nuit', title="🌙 Téléphone au lit",
                          color_discrete_sequence=COLORS)
            fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig2, use_container_width=True)

        with col_b:
            fig3 = px.scatter(df, x='smartphone_h', y='sommeil_h',
                              color='addiction_score', size='reseaux_h',
                              hover_data=['filiere', 'genre'],
                              title="📉 Smartphone vs Sommeil",
                              labels={'smartphone_h': 'Heures smartphone', 'sommeil_h': 'Heures sommeil'},
                              color_continuous_scale='Reds')
            fig3.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig3, use_container_width=True)

            fig4 = px.bar(df['impact_etudes'].value_counts().reset_index(),
                          x='impact_etudes', y='count', title="🎓 Impact sur les études",
                          color='impact_etudes', color_discrete_sequence=COLORS,
                          labels={'impact_etudes': 'Impact', 'count': 'Effectif'})
            fig4.update_layout(showlegend=False, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig4, use_container_width=True)

        st.subheader("⏱️ Temps moyen par activité numérique")
        activites = {
            "Smartphone": df['smartphone_h'].mean(),
            "Réseaux sociaux": df['reseaux_h'].mean(),
            "Streaming": df['streaming_h'].mean(),
            "Jeux vidéo": df['jeux_h'].mean(),
            "Travail PC": df['travail_pc_h'].mean()
        }
        fig5 = go.Figure(go.Bar(
            x=list(activites.keys()), y=list(activites.values()),
            marker_color=COLORS[:5],
            text=[f"{v:.1f}h" for v in activites.values()], textposition='outside'
        ))
        fig5.update_layout(yaxis_title="Heures/jour",
                           plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig5, use_container_width=True)

        st.subheader("🔗 Matrice de corrélation")
        num_cols = ["age","smartphone_h","reseaux_h","jeux_h","streaming_h","travail_pc_h","sommeil_h","addiction_score"]
        corr = df[num_cols].corr().round(2)
        fig6 = px.imshow(corr, text_auto=True, color_continuous_scale='RdBu_r', zmin=-1, zmax=1)
        fig6.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig6, use_container_width=True)

        st.subheader("📈 Statistiques descriptives")
        st.dataframe(df[num_cols].describe().round(2), use_container_width=True)

with tab3:
    df = load_data()
    if df.empty:
        st.info("Aucune donnée collectée.")
    else:
        st.subheader(f"{len(df)} entrée(s) enregistrée(s)")
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Télécharger (CSV)", csv, "habitudes_numeriques.csv",
                           "text/csv", use_container_width=True)
