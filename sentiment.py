# sentiment.py
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
import torch

# Initialize the sentiment analysis pipeline
try:
    # Load model and tokenizer
    model_name = "tabularisai/multilingual-sentiment-analysis"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    
    # Determine device
    if torch.backends.mps.is_available():
        device = "mps"  # Use MPS for Apple Silicon
    elif torch.cuda.is_available():
        device = 0  # Use CUDA if available
    else:
        device = -1  # Use CPU as fallback
    
    # Create pipeline
    sentiment_analyzer = pipeline(
        "sentiment-analysis",
        model=model,
        tokenizer=tokenizer,
        device=device,
        top_k=None  # Get all sentiment scores
    )
except Exception as e:
    print(f"Error initializing sentiment analyzer: {e}")
    sentiment_analyzer = None

def predict_sentiment(text):
    """Predict sentiment label: POSITIVE, NEUTRAL, or NEGATIVE based on detailed scores."""
    if not text or not isinstance(text, str):
        return "NEUTRAL"
    
    try:
        if sentiment_analyzer is None:
            return "NEUTRAL"
            
        # Get all sentiment scores
        results = sentiment_analyzer(text)[0]
        
        # Extract scores for each sentiment
        scores = {item['label']: item['score'] for item in results}
        
        # Calculate combined scores
        positive_score = scores.get('Very Positive', 0) + scores.get('Positive', 0)
        negative_score = scores.get('Very Negative', 0) + scores.get('Negative', 0)
        neutral_score = scores.get('Neutral', 0)
        
        # Determine sentiment based on highest score
        max_score = max(positive_score, negative_score, neutral_score)
        
        if max_score == positive_score and positive_score > 0.3:  # Threshold for positive
            return "POSITIVE"
        elif max_score == negative_score and negative_score > 0.3:  # Threshold for negative
            return "NEGATIVE"
        else:
            return "NEUTRAL"
            
    except Exception as e:
        print(f"Error in sentiment analysis: {e}")
        return "NEUTRAL"
