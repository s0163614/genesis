import mlflow
import mlflow.tensorflow
from tensorflow import keras
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout
from sklearn.model_selection import train_test_split
import pandas as pd
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

def load_data(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    return pd.DataFrame(lines, columns=["text"])

def preprocess_data(data):
   
    data['text'] = data['text'].str.replace('\n', ' ').str.strip()  
    
    
    data['label'] = data['text'].apply(lambda x: 1 if "необходимое условие" in x else 0)
    
    return data

def create_model(max_words, embedding_dim):
    model = keras.Sequential([
        Embedding(max_words, embedding_dim, input_length=30),  
        LSTM(50, return_sequences=True),
        Dropout(0.2),
        LSTM(50),
        Dropout(0.2),
        Dense(1, activation='sigmoid')
    ])
    
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

if __name__ == "__main__":
    mlflow.set_experiment("web_scraping_experiment")

    # Загрузка и предобработка данных
    df = load_data('templates/suda.txt')
    df = preprocess_data(df)

    
    tokenizer = Tokenizer(num_words=5000)
    tokenizer.fit_on_texts(df['text'])
    X = tokenizer.texts_to_sequences(df['text'])
    X = pad_sequences(X, maxlen=30)  

    y = df['label'].values
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Создание и обучение модели
    model = create_model(max_words=5000, embedding_dim=50)
    
    with mlflow.start_run():
        model.fit(X_train, y_train, epochs=10, verbose=1, validation_data=(X_test, y_test))

        # Логирование метрик
        loss, accuracy = model.evaluate(X_test, y_test, verbose=1)
        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("loss", loss)

        # Сохранение модели
        mlflow.tensorflow.log_model(model, artifact_path="model")
