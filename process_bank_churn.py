# -*- coding: utf-8 -*-
"""process_bank_churn

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1a6VpwjUte0osI9PFC9BPPpICPu2DyCGb
"""

# process_bank_churn.py

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

def preprocess_data(raw_df, target_col='Exited', scaler_numeric=True):
    # Обираємо колонки для роботи
    df = raw_df.drop(columns=['Surname'])  # Видаляємо колонку 'Surname'

    # Розділяємо на X та y
    X = df.drop(columns=[target_col])  # Видаляємо цільову колонку з набору ознак X
    y = df[target_col]

    # Розбиваємо на тренувальні та валідаційні набори
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

    # Визначаємо числові та категоріальні колонки з використанням X_train
    numeric_cols = X_train.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = X_train.select_dtypes(include=['object', 'category']).columns.tolist()

    # Підготовка даних з використанням Pipeline
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='mean'))
    ])

    if scaler_numeric:
        numeric_transformer.steps.append(('scaler', StandardScaler()))

    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_cols),
            ('cat', categorical_transformer, categorical_cols)
        ])

    # Підготовлені дані для тренувального та валідаційного наборів
    X_train_processed = preprocessor.fit_transform(X_train)
    X_val_processed = preprocessor.transform(X_val)

    # Отримуємо назви колонок після one-hot encoding
    input_cols = numeric_cols + list(preprocessor.named_transformers_['cat']['onehot'].get_feature_names_out(categorical_cols))

    return X_train_processed, y_train, X_val_processed, y_val, input_cols, preprocessor.named_transformers_['num'].named_steps.get('scaler'), preprocessor.named_transformers_['cat'].named_steps['onehot']

# Example usage:
# raw_df = pd.read_csv('path_to_your_csv_file.csv')
# X_train, train_targets, X_val, val_targets, input_cols, scaler, encoder = preprocess_data(raw_df)


def preprocess_new_data(new_data, scaler, encoder, numeric_cols, categorical_cols):
    # Видаляємо колонку 'Exited', якщо вона є у нових даних
    if 'Exited' in new_data.columns:
        new_data = new_data.drop(columns=['Exited'])

    # Відокремлюємо числові та категоріальні ознаки з нових даних
    numeric_features = new_data[numeric_cols] if numeric_cols else np.array([])
    categorical_features = new_data[categorical_cols] if categorical_cols else np.array([])

    # Масштабуємо числові ознаки, якщо є скалятор
    if scaler and numeric_features.shape[0] > 0:
        numeric_features = scaler.transform(numeric_features)

    # Кодуємо категоріальні ознаки, якщо є енкодер
    if encoder and categorical_features.shape[0] > 0:
        categorical_features = encoder.transform(categorical_features)

    # Об'єднуємо числові та категоріальні ознаки
    if categorical_features.shape[0] > 0:
        X_processed = np.hstack((numeric_features, categorical_features.toarray()))
    else:
        X_processed = numeric_features

    return X_processed