import streamlit as st
import joblib
import pickle
import pandas as pd
import re
import regex
import string 
import random
import nltk
import pickle
import os
from underthesea import word_tokenize
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import json

# Page configuration
st.set_page_config(
    page_title="Vietnamese Student Feedback Sentiment Analysis",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sentiment mapping
SENTIMENT_MAP = {0: "Negative", 1: "Neutral", 2: "Positive"}
SENTIMENT_EMOJIS = {0: "😞", 1: "😐", 2: "😊"}
SENTIMENT_COLORS = {0: "#FF6B6B", 1: "#FFD93D", 2: "#6BCF7F"}
SENTIMENT_COLORS_DARK = {0: "#E74C3C", 1: "#F39C12", 2: "#27AE60"}

def inject_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');

        /* Global Styles */
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-family: 'Inter', sans-serif;
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Main container */
        .main-header {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            padding: 2rem;
            margin-bottom: 2rem;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .main-header h1 {
            color: white;
            font-size: 2.5rem;
            font-weight: 700;
            margin: 0;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        
        .main-header p {
            color: rgba(255, 255, 255, 0.8);
            font-size: 1.1rem;
            margin: 0.5rem 0 0 0;
        }
        
        /* Glass card effect */
        .glass-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(15px);
            border-radius: 15px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
        }
        
        /* Button styling */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 25px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            color: white;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }
        
        .stButton > button:hover {
            background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
        }
        
        /* Example buttons styling */
        .example-btn {
            background: linear-gradient(45deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%);
            border: none;
            border-radius: 15px;
            padding: 0.75rem 1rem;
            margin: 0.25rem 0;
            font-weight: 500;
            color: #2c3e50;
            transition: all 0.3s ease;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            width: 100%;
            text-align: left;
            cursor: pointer;
        }
        
        .example-btn:hover {
            background: linear-gradient(45deg, #fecfef 0%, #ff9a9e 50%, #ff9a9e 100%);
            transform: translateY(-1px);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }
        
        /* Primary button different gradient */
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }
        
        .stButton > button[kind="primary"]:hover {
            background: linear-gradient(135deg, #f5576c 0%, #f093fb 100%);
        }
        
        /* Metrics styling */
        div[data-testid="metric-container"] {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 1rem;
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }
        
        /* Text input styling */
        .stTextArea textarea {
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 10px;
            color: #2c3e50;
            backdrop-filter: blur(10px);
        }
        
        .stTextArea textarea::placeholder {
            color: rgba(0, 0, 0, 0.6);
        }
        
        /* Selectbox styling */
        .stSelectbox > div > div {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 0.5rem 1rem;
            margin-right: 0.5rem;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .stTabs [aria-selected="true"] {
            background: rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.4);
        }
        
        /* Success/Error messages */
        .stSuccess {
            background: rgba(108, 207, 127, 0.2);
            border: 1px solid #6BCF7F;
            border-radius: 10px;
        }
        
        .stError {
            background: rgba(255, 107, 107, 0.2);
            border: 1px solid #FF6B6B;
            border-radius: 10px;
        }
        
        .stWarning {
            background: rgba(255, 217, 61, 0.2);
            border: 1px solid #FFD93D;
            border-radius: 10px;
        }
        
        /* Custom result card */
        .result-card {
            background: linear-gradient(135deg, rgba(255,255,255,0.2), rgba(255,255,255,0.1));
            backdrop-filter: blur(20px);
            border-radius: 15px;
            padding: 2rem;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.3);
            margin: 1rem 0;
        }
        
        .result-card h2 {
            color: white;
            font-size: 2rem;
            margin: 0;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        
        /* Stats container */
        .stats-container {
            display: flex;
            justify-content: space-around;
            margin: 1rem 0;
        }
        
        .stat-item {
            text-align: center;
            color: white;
        }
        
        .stat-number {
            font-size: 2rem;
            font-weight: 700;
            color: #4ECDC4;
        }
        
        .stat-label {
            font-size: 0.9rem;
            opacity: 0.8;
        }
        
        /* Animation classes */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .animate-fade-in {
            animation: fadeInUp 0.6s ease-out;
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .main-header h1 {
                font-size: 2rem;
            }
            
            .glass-card {
                padding: 1rem;
            }
        }
        </style>
    """, unsafe_allow_html=True)

def clean_text(text):
    """Clean and preprocess Vietnamese text"""
    if pd.isna(text) or text == '' or not isinstance(text, str):
        return ''
    
    text = str(text)
    text = text.lower()
    text = re.sub(r'[^\w\s\u00C0-\u1EF9\u0102\u0103\u0110\u0111\u0128\u0129\u0168\u0169\u01A0\u01A1\u01AF\u01B0]', ' ', text)
    text = re.sub(r'(.)\1{2,}', r'\1', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    if not text or text.isspace():
        return ''
    text = re.sub(r'\s+', ' ', text).strip()
    text = word_tokenize(text, format="text")
    
    return text

@st.cache_resource
def load_models_and_vectorizer():
    """Load all models and vectorizer"""
    models = {}
    vectorizer = None
    model_info = {}
    
    try:
        # Load vectorizer
        with open('bow_vectorizer.pkl', 'rb') as f:
            vectorizer = pickle.load(f)
        
        # Load models with their info
        model_files = {
            'XGBoost': ('xgboost_bow_model.pkl', 'Extreme Gradient Boosting'),
            'Logistic Regression': ('logistic_regression_bow_model.pkl', 'Linear Classification'),
            'SVM': ('svm_bow_model.pkl', 'Support Vector Machine'),
            'Naive Bayes': ('naive_bayes_bow_model.pkl', 'Probabilistic Classifier'),
            'Stacking': ('ml_ensemble_bow_model.pkl', 'Ensemble Method')
        }
        
        for name, (file, description) in model_files.items():
            try:
                models[name] = joblib.load(file)
                model_info[name] = description
            except FileNotFoundError:
                st.warning(f"Model file {file} not found. Skipping {name}.")
                continue
        
    except FileNotFoundError as e:
        st.error(f"Vectorizer file not found: {e}")
    except Exception as e:
        st.error(f"Error loading models: {str(e)}")
    
    return models, vectorizer, model_info

def predict_sentiment(text, model_name, models, vectorizer):
    """Predict sentiment with confidence score"""
    if not text.strip():
        return None, None, "Please enter some text"
    
    # Clean the text
    cleaned_text = clean_text(text)
    
    if not cleaned_text.strip():
        return None, None, "Text becomes empty after cleaning"
    
    try:
        # Transform text using BoW vectorizer
        text_vectorized = vectorizer.transform([cleaned_text])
        
        # Make prediction
        model = models[model_name]
        prediction = model.predict(text_vectorized)[0]
        
        # Get prediction probability if available
        probabilities = None
        confidence = None
        if hasattr(model, 'predict_proba'):
            probabilities = model.predict_proba(text_vectorized)[0]
            confidence = max(probabilities)
        
        return prediction, probabilities, confidence
    
    except Exception as e:
        return None, None, f"Error during prediction: {str(e)}"

def create_confidence_chart(probabilities):
    """Create a confidence chart using plotly with white text"""
    if probabilities is None:
        return None
    
    labels = ['Negative 😞', 'Neutral 😐', 'Positive 😊']
    colors = ['#FF6B6B', '#FFD93D', '#6BCF7F']
    
    fig = go.Figure(data=[
        go.Bar(
            x=labels,
            y=probabilities,
            marker_color=colors,
            text=[f'{p:.1%}' for p in probabilities],
            textposition='auto',
            textfont=dict(color='white', size=14)
        )
    ])
    
    fig.update_layout(
        title=dict(
            text="Confidence Scores by Sentiment",
            font=dict(color='white', size=16)
        ),
        xaxis=dict(
            title=dict(text="Sentiment", font=dict(color='white')),
            tickfont=dict(color='white')
        ),
        yaxis=dict(
            title=dict(text="Probability", font=dict(color='white')),
            tickfont=dict(color='white')
        ),
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=400
    )
    
    return fig

def create_sentiment_pie_chart(history):
    """Create pie chart from prediction history with white text"""
    if not history:
        return None
    
    sentiment_counts = {0: 0, 1: 0, 2: 0}
    for item in history:
        sentiment_counts[item['prediction']] += 1
    
    labels = ['Negative 😞', 'Neutral 😐', 'Positive 😊']
    values = [sentiment_counts[0], sentiment_counts[1], sentiment_counts[2]]
    colors = ['#FF6B6B', '#FFD93D', '#6BCF7F']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker_colors=colors,
        textinfo='label+percent',
        textfont_size=12,
        textfont_color='white'
    )])
    
    fig.update_layout(
        title=dict(
            text="Sentiment Distribution",
            font=dict(color='white', size=16)
        ),
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=400,
        legend=dict(font=dict(color='white'))
    )
    
    return fig

def main():
    # Inject custom CSS
    inject_custom_css()
    
    # Initialize session state
    if 'prediction_history' not in st.session_state:
        st.session_state.prediction_history = []
    if 'total_predictions' not in st.session_state:
        st.session_state.total_predictions = 0
    
    # Main header
    st.markdown("""
        <div class="main-header animate-fade-in">
            <h1><i class="fas fa-graduation-cap"></i> Vietnamese Student Feedback Sentiment Analysis</h1>
            <p>Advanced AI-powered sentiment analysis for Vietnamese educational feedback</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Load models and vectorizer
    models, vectorizer, model_info = load_models_and_vectorizer()
    
    if not models or vectorizer is None:
        st.error("❌ Failed to load models or vectorizer. Please check file paths.")
        st.stop()
    
    # Sidebar
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")
        
        # Model selection
        available_models = list(models.keys())
        selected_model = st.selectbox(
            "🤖 Choose AI Model:",
            available_models,
            index=0,
            help="Select the machine learning model for prediction"
        )
        
        # Model information
        st.info(f"**Model:** {selected_model}\n\n**Type:** {model_info.get(selected_model, 'N/A')}\n\n**Vectorizer:** Bag of Words")
        
        # Settings
        st.markdown("## 📊 Display Settings")
        show_confidence = st.checkbox("Show Confidence Scores", value=True)
        show_cleaned_text = st.checkbox("Show Cleaned Text", value=False)
        show_charts = st.checkbox("Show Charts", value=True)
        
        # Statistics
        st.markdown("## 📈 Session Statistics")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Predictions", st.session_state.total_predictions)
        with col2:
            if st.session_state.prediction_history:
                avg_confidence = sum(item.get('confidence', 0) for item in st.session_state.prediction_history if item.get('confidence')) / len(st.session_state.prediction_history)
                st.metric("Avg Confidence", f"{avg_confidence:.1%}")
            else:
                st.metric("Avg Confidence", "0%")
        
        # Clear history button
        if st.button("🗑️ Clear History", type="secondary"):
            st.session_state.prediction_history = []
            st.session_state.total_predictions = 0
            st.rerun()
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🔮 Predict", "📊 Analytics", "📝 Batch Analysis", "ℹ️ About"])
    
    with tab1:
        # Prediction interface
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 💬 Enter Student Feedback")
            
            # Text input options
            input_method = st.radio(
                "Input method:",
                ["Text Area", "File Upload"],
                horizontal=True
            )
            
            user_input = ""
            if input_method == "Text Area":
                # Kiểm tra nếu có example được chọn
                default_value = st.session_state.get('example_text', '')
                user_input = st.text_area(
                    "Vietnamese student feedback:",
                    value=default_value,
                    placeholder="Ví dụ: Giáo viên dạy rất hay và dễ hiểu, tôi rất thích môn học này...",
                    height=150,
                    help="Enter Vietnamese text for sentiment analysis"
                )
            else:
                uploaded_file = st.file_uploader(
                    "Upload text file:",
                    type=['txt'],
                    help="Upload a .txt file containing Vietnamese text"
                )
                if uploaded_file is not None:
                    user_input = str(uploaded_file.read(), "utf-8")
                    st.text_area("File content:", user_input, height=100, disabled=True)
            
            # Predict button
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            with col_btn2:
                predict_btn = st.button("🔮 Analyze Sentiment", type="primary", use_container_width=True)
        
        with col2:
            st.markdown("### 🎯 Quick Examples")
            examples = [
                "Môn học này khó quá, tôi không hiểu gì cả",
                "Bài giảng bình thường, không có gì đặc biệt"
            ]
            
            st.markdown("""
                <style>
                .example-container {
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 10px;
                    padding: 1rem;
                    margin: 0.5rem 0;
                }
                </style>
            """, unsafe_allow_html=True)
            
            for i, example in enumerate(examples):
                # Hiển thị text của example
                st.markdown(f"""
                    <div class="example-container">
                        <small style="color: rgba(255,255,255,0.7);">Example {i+1}:</small><br>
                        <span style="color: white; font-weight: 500;">"{example}"</span>
                    </div>
                """, unsafe_allow_html=True)
                
                # Button để chọn example
                if st.button(f"✨ Use Example {i+1}", key=f"example_{i}", use_container_width=True):
                    st.session_state.example_text = example
                    st.rerun()  # Refresh để cập nhật textbox
            
        
        # Prediction results
        if predict_btn and user_input.strip():
            with st.spinner("🤖 Analyzing sentiment..."):
                time.sleep(0.5)  # Small delay for better UX
                prediction, probabilities, confidence = predict_sentiment(
                    user_input, selected_model, models, vectorizer
                )
            
            if prediction is not None:
                # Store in history
                st.session_state.prediction_history.append({
                    'text': user_input[:100] + "..." if len(user_input) > 100 else user_input,
                    'prediction': prediction,
                    'confidence': confidence,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'model': selected_model
                })
                st.session_state.total_predictions += 1
                
                # Display results
                sentiment_label = SENTIMENT_MAP[prediction]
                sentiment_emoji = SENTIMENT_EMOJIS[prediction]
                sentiment_color = SENTIMENT_COLORS[prediction]
                
                # Main result card
                st.markdown(
                    f"""
                    <div class="result-card animate-fade-in">
                        <h2>{sentiment_emoji} {sentiment_label}</h2>
                        <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0;">
                            Sentiment Classification Result
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                # Metrics row
                if show_confidence and confidence is not None:
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("🎯 Confidence", f"{confidence:.1%}")
                    with col2:
                        st.metric("🤖 Model", selected_model)
                    with col3:
                        st.metric("📝 Text Length", len(user_input))
                    with col4:
                        st.metric("⏱️ Processing", "< 1s")
                
                # Confidence chart
                if show_charts and probabilities is not None:
                    fig = create_confidence_chart(probabilities)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                
                # Show cleaned text
                if show_cleaned_text:
                    cleaned = clean_text(user_input)
                    if cleaned != user_input.lower():
                        with st.expander("🧹 View Text Processing"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.text_area("Original Text:", user_input, height=100, disabled=True)
                            with col2:
                                st.text_area("Cleaned Text:", cleaned, height=100, disabled=True)
            
            else:
                st.error(f"❌ Prediction failed: {confidence}")
        
        elif predict_btn:
            st.warning("⚠️ Please enter some text to analyze.")
    
    with tab2:
        # Analytics dashboard
        st.markdown("### 📊 Analytics Dashboard")
        
        if st.session_state.prediction_history:
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            positive_count = sum(1 for item in st.session_state.prediction_history if item['prediction'] == 2)
            negative_count = sum(1 for item in st.session_state.prediction_history if item['prediction'] == 0)
            neutral_count = sum(1 for item in st.session_state.prediction_history if item['prediction'] == 1)
            
            with col1:
                st.metric("😊 Positive", positive_count)
            with col2:
                st.metric("😞 Negative", negative_count)
            with col3:
                st.metric("😐 Neutral", neutral_count)
            with col4:
                avg_conf = sum(item.get('confidence', 0) for item in st.session_state.prediction_history if item.get('confidence')) / len(st.session_state.prediction_history)
                st.metric("Avg Confidence", f"{avg_conf:.1%}")
            
            # Charts
            col1, col2 = st.columns(2)
            
            with col1:
                # Pie chart
                pie_fig = create_sentiment_pie_chart(st.session_state.prediction_history)
                if pie_fig:
                    st.plotly_chart(pie_fig, use_container_width=True)
            
            with col2:
                # Timeline chart
                df_history = pd.DataFrame(st.session_state.prediction_history)
                df_history['datetime'] = pd.to_datetime(df_history['timestamp'])
                
                fig = px.scatter(
                    df_history, 
                    x='datetime', 
                    y='prediction',
                    color='prediction',
                    color_discrete_map={0: '#FF6B6B', 1: '#FFD93D', 2: '#6BCF7F'},
                    title="Prediction Timeline",
                    template='plotly_dark'
                )
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # History table
            st.markdown("### 📋 Prediction History")
            df_display = pd.DataFrame(st.session_state.prediction_history)
            df_display['Sentiment'] = df_display['prediction'].map(lambda x: f"{SENTIMENT_EMOJIS[x]} {SENTIMENT_MAP[x]}")
            df_display['Confidence'] = df_display['confidence'].map(lambda x: f"{x:.1%}" if x else "N/A")
            
            st.dataframe(
                df_display[['timestamp', 'text', 'Sentiment', 'Confidence', 'model']].rename(columns={
                    'timestamp': 'Time',
                    'text': 'Text',
                    'model': 'Model'
                }),
                use_container_width=True
            )
            
        else:
            st.info("📈 No predictions yet. Start analyzing some text to see analytics!")
    
    with tab3:
        # Batch analysis
        st.markdown("### 📝 Batch Analysis")
        st.info("Upload a CSV file with Vietnamese text for batch sentiment analysis")
        
        uploaded_file = st.file_uploader(
            "Choose CSV file:",
            type=['csv'],
            help="CSV file should have a column with Vietnamese text"
        )
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                st.write("File preview:")
                st.dataframe(df.head())
                
                # Column selection
                text_column = st.selectbox("Select text column:", df.columns)
                
                if st.button("🚀 Start Batch Analysis"):
                    progress_bar = st.progress(0)
                    results = []
                    
                    for i, text in enumerate(df[text_column]):
                        if pd.notna(text):
                            pred, probs, conf = predict_sentiment(str(text), selected_model, models, vectorizer)
                            results.append({
                                'original_text': text,
                                'prediction': pred,
                                'sentiment': SENTIMENT_MAP[pred] if pred is not None else 'Error',
                                'confidence': conf
                            })
                        else:
                            results.append({
                                'original_text': text,
                                'prediction': None,
                                'sentiment': 'Empty',
                                'confidence': None
                            })
                        
                        progress_bar.progress((i + 1) / len(df))
                    
                    # Display results
                    results_df = pd.DataFrame(results)
                    st.success(f"✅ Analysis complete! Processed {len(results)} texts.")
                    
                    # Summary
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("😊 Positive", len(results_df[results_df['prediction'] == 2]))
                    with col2:
                        st.metric("😞 Negative", len(results_df[results_df['prediction'] == 0]))
                    with col3:
                        st.metric("😐 Neutral", len(results_df[results_df['prediction'] == 1]))
                    
                    # Download results
                    csv = results_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Results",
                        data=csv,
                        file_name=f"sentiment_analysis_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                    
                    st.dataframe(results_df, use_container_width=True)
                    
            except Exception as e:
                st.error(f"❌ Error processing file: {str(e)}")
    
    with tab4:
        # About section
        st.markdown("### ℹ️ About This Application")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **🎯 Purpose**
            
            This application provides advanced sentiment analysis for Vietnamese student feedback using multiple machine learning models.
            
            **🤖 Available Models**
            - **XGBoost**: Gradient boosting framework
            - **Logistic Regression**: Linear classification
            - **SVM**: Support Vector Machine
            - **Naive Bayes**: Probabilistic classifier
            - **Stacking**: Ensemble method
            
            **📊 Features**
            - Real-time sentiment prediction
            - Confidence scoring
            - Batch processing
            - Analytics dashboard
            - Export functionality
            """)
        
        with col2:
            st.markdown("""
            **🛠️ Technical Details**
            
            - **Preprocessing**: Vietnamese text tokenization using underthesea
            - **Vectorization**: Bag of Words (BoW)
            - **Languages**: Vietnamese text support
            - **Output**: 3-class sentiment (Positive, Neutral, Negative)
            
            **📈 Performance Metrics**
            - Accuracy scores available for each model
            - Confidence intervals provided
            - Real-time processing
            
            **🔒 Privacy**
            - No data is stored permanently
            - Session-based history only
            - Local processing
            """)
        
        # Version info
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info("**Version**: 2.0.0")
        with col2:
            st.info("**Last Updated**: 2024")
        with col3:
            st.info("**Language**: Vietnamese")

if __name__ == "__main__":
    main()