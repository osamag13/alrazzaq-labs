import tensorflow as tf
from tensorflow.keras.datasets import mnist
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, Dense, Flatten
import numpy as np

# 1. Load and preprocess the MNIST dataset
(x_train, y_train), (x_test, y_test) = mnist.load_data()
x_train, x_test = x_train / 255.0, x_test / 255.0  # Normalize

# 2. Build the Model
model = Sequential([
    Input(shape=(28, 28)),  # ✅ Recommended way in Keras 3
    Flatten(),
    Dense(128, activation='relu'),
    Dense(10, activation='softmax')
])

# 3. Compile the Model
model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

# 4. Train the Model
print("\nTraining the model...")
model.fit(x_train, y_train, epochs=5, batch_size=32, verbose=1)

# 5. Save the Model using Keras 3 native `.keras` format
model.save('my_model.keras')
print("\nModel saved as 'my_model.keras'")

# 6. Load the Model
print("\nLoading the saved model...")
loaded_model = tf.keras.models.load_model('my_model.keras')
print("Model loaded successfully!")

# 7. Evaluate the loaded model
loss, accuracy = loaded_model.evaluate(x_test, y_test, verbose=0)
print(f"\nTest Accuracy: {accuracy:.4f}")

# 8. Make a Prediction
sample_image = x_test[0].reshape(1, 28, 28)  # Take first test image
prediction = loaded_model.predict(sample_image)
predicted_class = np.argmax(prediction)

print(f"\nPredicted Class: {predicted_class}")
print(f"Actual Class: {y_test[0]}")
