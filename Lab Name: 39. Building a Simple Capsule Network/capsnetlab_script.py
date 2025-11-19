import tensorflow as tf
from tensorflow.keras import layers, models, datasets
import numpy as np
import matplotlib.pyplot as plt

class CapsuleLayer(layers.Layer):
    def __init__(self, num_capsules, dim_capsules, **kwargs):
        super().__init__(**kwargs)
        self.num_capsules = num_capsules
        self.dim_capsules = dim_capsules

    def build(self, input_shape):
        num_caps_in = input_shape[1]
        dim_caps_in = input_shape[2]

        self.kernel = self.add_weight(
            name='capsule_kernel',
            shape=(num_caps_in, self.num_capsules, self.dim_capsules, dim_caps_in),
            initializer='glorot_uniform',
            trainable=True
        )

    def call(self, inputs):
        x = tf.expand_dims(inputs, 2)
        x = tf.expand_dims(x, 3)
        u_hat = tf.reduce_sum(self.kernel * x, axis=-1)
        return tf.reduce_mean(u_hat, axis=1)

def create_capsnet(input_shape):
    inputs = layers.Input(shape=input_shape)

    x = layers.Conv2D(64, 9, activation='relu')(inputs)
    x = layers.Conv2D(64, 9, activation='relu')(x)

    # Conv output: (12, 12, 64) → reshape into (144, 64)
    x = layers.Reshape((144, 64))(x)

    capsule = CapsuleLayer(num_capsules=10, dim_capsules=16)(x)
    outputs = layers.Lambda(lambda t: tf.norm(t, axis=-1))(capsule)

    return models.Model(inputs, outputs)

capsnet = create_capsnet((28, 28, 1))
capsnet.summary()

(train_images, train_labels), (test_images, test_labels) = datasets.mnist.load_data()
train_images = train_images.reshape(-1, 28, 28, 1) / 255.
test_images = test_images.reshape(-1, 28, 28, 1) / 255.

capsnet.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

history = capsnet.fit(
    train_images, train_labels,
    batch_size=64,
    epochs=3,
    validation_split=0.1
)

loss, acc = capsnet.evaluate(test_images, test_labels)
print("Test Accuracy:", acc)

# PLOTS
plt.plot(history.history['loss'], label='loss')
plt.plot(history.history['val_loss'], label='val_loss')
plt.legend()
plt.show()

plt.plot(history.history['accuracy'], label='acc')
plt.plot(history.history['val_accuracy'], label='val_acc')
plt.legend()
plt.show()
