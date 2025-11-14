import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


# =========================================================
# CONFIGURATION
# =========================================================

ENC_FEATURE_DIM = 16
DEC_FEATURE_DIM = 16
ENC_UNITS = 32
DEC_UNITS = 32
OUTPUT_VOCAB_SIZE = 12
OUTPUT_LENGTH = 6
ENC_SEQ_LEN = 7
DEC_SEQ_LEN = OUTPUT_LENGTH


# =========================================================
# SIMPLE ATTENTION LAYER
# =========================================================

class SimpleAttention(tf.keras.layers.Layer):
    def __init__(self, units):
        super(SimpleAttention, self).__init__()
        self.W_a = tf.keras.layers.Dense(units)
        self.U_a = tf.keras.layers.Dense(units)
        self.V_a = tf.keras.layers.Dense(1)

    def call(self, encoder_states, decoder_hidden):
        decoder_hidden_exp = tf.expand_dims(decoder_hidden, 1)
        score = self.V_a(
            tf.nn.tanh(self.W_a(encoder_states) + self.U_a(decoder_hidden_exp))
        )
        attention_weights = tf.nn.softmax(score, axis=1)
        context_vector = attention_weights * encoder_states
        context_vector = tf.reduce_sum(context_vector, axis=1)
        return context_vector, attention_weights


# =========================================================
# BUILD SEQ2SEQ WITH ATTENTION
# =========================================================

encoder_inputs = tf.keras.layers.Input(shape=(ENC_SEQ_LEN, ENC_FEATURE_DIM))
encoder_lstm = tf.keras.layers.LSTM(ENC_UNITS, return_sequences=True, return_state=True)
encoder_outputs, state_h, state_c = encoder_lstm(encoder_inputs)

decoder_inputs = tf.keras.layers.Input(shape=(DEC_SEQ_LEN, DEC_FEATURE_DIM))
decoder_lstm = tf.keras.layers.LSTM(DEC_UNITS, return_sequences=True, return_state=True)

attention = SimpleAttention(ENC_UNITS)

step_extract = tf.keras.layers.Lambda(lambda x: x[:, 0, :])
expand_time = tf.keras.layers.Lambda(lambda x: tf.expand_dims(x, axis=1))
concat_layer = tf.keras.layers.Concatenate()
output_dense = tf.keras.layers.Dense(OUTPUT_VOCAB_SIZE, activation="softmax")

all_outputs = []
all_attentions = []

decoder_state_h = state_h
decoder_state_c = state_c

for t in range(OUTPUT_LENGTH):

    decoder_input_t = tf.keras.layers.Lambda(lambda x, i=t: x[:, i:i+1, :])(decoder_inputs)

    decoder_output_seq, decoder_state_h, decoder_state_c = decoder_lstm(
        decoder_input_t, initial_state=[decoder_state_h, decoder_state_c]
    )

    decoder_output_t = step_extract(decoder_output_seq)

    context_vector, attention_weights = attention(encoder_outputs, decoder_state_h)

    concat = concat_layer([decoder_output_t, context_vector])
    dense_output = output_dense(concat)

    dense_output_time = expand_time(dense_output)
    all_outputs.append(dense_output_time)

    # FIXED: reshape attention to (batch, 1, ENC_SEQ_LEN)
    att_time = tf.keras.layers.Lambda(
        lambda x: tf.reshape(x, (-1, 1, ENC_SEQ_LEN))
    )(attention_weights[..., 0])
    all_attentions.append(att_time)

decoder_outputs = tf.keras.layers.Concatenate(axis=1, name="decoder_outputs")(all_outputs)
attention_outputs = tf.keras.layers.Concatenate(axis=1, name="attention_outputs")(all_attentions)

model = tf.keras.Model(
    inputs=[encoder_inputs, decoder_inputs],
    outputs=[decoder_outputs, attention_outputs]
)


# =========================================================
# COMPILE MODEL
# =========================================================

model.compile(
    optimizer="adam",
    loss=["sparse_categorical_crossentropy", None]  # no loss for attention
)

model.summary()


# =========================================================
# GENERATE DUMMY DATA
# =========================================================

batch_size = 32
num_samples = 200

X_encoder = np.random.rand(num_samples, ENC_SEQ_LEN, ENC_FEATURE_DIM).astype("float32")
X_decoder = np.random.rand(num_samples, DEC_SEQ_LEN, DEC_FEATURE_DIM).astype("float32")
y = np.random.randint(0, OUTPUT_VOCAB_SIZE, size=(num_samples, OUTPUT_LENGTH, 1))


# =========================================================
# TRAIN MODEL
# =========================================================

print("\nTraining model on dummy data...\n")

model.fit(
    [X_encoder, X_decoder],
    [y, None],
    epochs=2,
    batch_size=batch_size
)

print("\nModel training completed.\n")


# =========================================================
# INFERENCE
# =========================================================

sample_enc = X_encoder[:1]
sample_dec = X_decoder[:1]

logits, attentions = model.predict([sample_enc, sample_dec])

# correct attention shape: (OUTPUT_LENGTH, ENC_SEQ_LEN)
att_matrix = attentions[0]


# =========================================================
# ATTENTION PLOT FUNCTION
# =========================================================

def plot_attention(attention_matrix, input_tokens, output_tokens):
    plt.figure(figsize=(10, 8))
    sns.heatmap(attention_matrix,
                xticklabels=input_tokens,
                yticklabels=output_tokens,
                cmap="viridis",
                annot=True,
                fmt=".2f")

    plt.xlabel("Encoder Input Sequence")
    plt.ylabel("Decoder Output Sequence")
    plt.title("Attention Heatmap")
    plt.show()


# =========================================================
# PLOT ATTENTION
# =========================================================

input_tokens = [f"in_{i}" for i in range(ENC_SEQ_LEN)]
output_tokens = [f"out_{i}" for i in range(OUTPUT_LENGTH)]

plot_attention(att_matrix, input_tokens, output_tokens)
