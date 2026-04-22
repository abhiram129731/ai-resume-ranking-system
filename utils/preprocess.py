import re
import nltk
from nltk.corpus import stopwords

# 🔥 Download only if not already present
try:
    stop_words = set(stopwords.words('english'))
except LookupError:
    nltk.download('stopwords')
    stop_words = set(stopwords.words('english'))

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z ]', '', text)

    words = text.split()
    words = [w for w in words if w not in stop_words]

    return " ".join(words)
