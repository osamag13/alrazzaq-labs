import torch
import torch.nn as nn
import random

# -----------------------------
#   PART 1 — YOUR MODELS
# -----------------------------

class EncoderRNN(nn.Module):
    def __init__(self, input_size, hidden_size):
        super(EncoderRNN, self).__init__()
        self.hidden_size = hidden_size
        self.embedding = nn.Embedding(input_size, hidden_size)
        self.rnn = nn.GRU(hidden_size, hidden_size)

    def forward(self, input, hidden):
        embedded = self.embedding(input).view(1, 1, -1)
        output, hidden = self.rnn(embedded, hidden)
        return output, hidden

    def initHidden(self):
        return torch.zeros(1, 1, self.hidden_size)


class DecoderRNN(nn.Module):
    def __init__(self, hidden_size, output_size):
        super(DecoderRNN, self).__init__()
        self.hidden_size = hidden_size
        self.embedding = nn.Embedding(output_size, hidden_size)
        self.rnn = nn.GRU(hidden_size, hidden_size)
        self.out = nn.Linear(hidden_size, output_size)
        self.softmax = nn.LogSoftmax(dim=1)

    def forward(self, input, hidden):
        output = self.embedding(input).view(1, 1, -1)
        output = nn.functional.relu(output)
        output, hidden = self.rnn(output, hidden)
        output = self.softmax(self.out(output[0]))
        return output, hidden

    def initHidden(self):
        return torch.zeros(1, 1, self.hidden_size)


# -----------------------------
#   PART 2 — READY DATASET
# -----------------------------

SOS_token = 0
EOS_token = 1

class Lang:
    def __init__(self):
        self.word2index = {"SOS": 0, "EOS": 1}
        self.index2word = {0: "SOS", 1: "EOS"}
        self.n_words = 2

    def addSentence(self, sentence):
        for w in sentence.split(" "):
            self.addWord(w)

    def addWord(self, word):
        if word not in self.word2index:
            self.word2index[word] = self.n_words
            self.index2word[self.n_words] = word
            self.n_words += 1


def tensorFromSentence(lang, sentence):
    idxs = [lang.word2index[w] for w in sentence.split(" ")]
    idxs.append(EOS_token)
    return torch.tensor(idxs, dtype=torch.long).view(-1, 1)


# Simple numeric dataset (input → sum)
pairs = [
    ("1 2", "3"),
    ("2 3", "5"),
    ("3 4", "7"),
    ("4 5", "9"),
    ("5 6", "11")
]

# Build vocab
input_lang = Lang()
output_lang = Lang()

for inp, out in pairs:
    input_lang.addSentence(inp)
    output_lang.addSentence(out)

training_pairs = [
    (tensorFromSentence(input_lang, inp), tensorFromSentence(output_lang, out))
    for inp, out in pairs
]


# -----------------------------
#   PART 3 — TRAINING
# -----------------------------

def train_step(input_tensor, target_tensor, encoder, decoder,
               encoder_optimizer, decoder_optimizer, criterion,
               max_length=10):

    encoder_hidden = encoder.initHidden()

    encoder_optimizer.zero_grad()
    decoder_optimizer.zero_grad()

    loss = 0

    # Encode input
    for ei in range(input_tensor.size(0)):
        encoder_output, encoder_hidden = encoder(
            input_tensor[ei], encoder_hidden
        )

    # Start decoder with SOS
    decoder_input = torch.tensor([[SOS_token]])
    decoder_hidden = encoder_hidden

    # Decode
    for di in range(target_tensor.size(0)):
        decoder_output, decoder_hidden = decoder(
            decoder_input, decoder_hidden
        )
        topv, topi = decoder_output.topk(1)
        decoder_input = topi.detach()

        loss += criterion(decoder_output, target_tensor[di])
        if decoder_input.item() == EOS_token:
            break

    loss.backward()

    encoder_optimizer.step()
    decoder_optimizer.step()

    return loss.item() / target_tensor.size(0)


# Initialize models
hidden_size = 32
encoder = EncoderRNN(input_lang.n_words, hidden_size)
decoder = DecoderRNN(hidden_size, output_lang.n_words)

encoder_optimizer = torch.optim.SGD(encoder.parameters(), lr=0.01)
decoder_optimizer = torch.optim.SGD(decoder.parameters(), lr=0.01)

criterion = nn.NLLLoss()

# Train for several epochs
for epoch in range(2000):
    input_tensor, target_tensor = random.choice(training_pairs)
    loss = train_step(
        input_tensor, target_tensor,
        encoder, decoder,
        encoder_optimizer, decoder_optimizer,
        criterion
    )
    if epoch % 200 == 0:
        print(f"Epoch {epoch} Loss = {loss:.4f}")


# -----------------------------
#   PART 4 — EVALUATION
# -----------------------------

def evaluate(encoder, decoder, sentence, max_length=10):
    with torch.no_grad():
        input_tensor = tensorFromSentence(input_lang, sentence)
        encoder_hidden = encoder.initHidden()

        # Encode
        for ei in range(input_tensor.size()[0]):
            encoder_output, encoder_hidden = encoder(
                input_tensor[ei], encoder_hidden
            )

        # Decode
        decoder_input = torch.tensor([[SOS_token]])
        decoder_hidden = encoder_hidden
        decoded_words = []

        for di in range(max_length):
            decoder_output, decoder_hidden = decoder(
                decoder_input, decoder_hidden
            )
            topv, topi = decoder_output.topk(1)

            if topi.item() == EOS_token:
                decoded_words.append("<EOS>")
                break
            else:
                decoded_words.append(output_lang.index2word[topi.item()])

            decoder_input = topi.detach()

        return decoded_words


# -----------------------------
#   PART 5 — SHOW OUTPUT
# -----------------------------

tests = ["1 2", "2 3", "5 6", "3 4"]

for t in tests:
    result = evaluate(encoder, decoder, t)
    print(f"Input: {t:5s}  → Output:", " ".join(result))
