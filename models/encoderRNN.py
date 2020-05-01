import torch.nn as nn

supported_rnns = {
    'lstm': nn.LSTM,
    'gru': nn.GRU,
    'rnn': nn.RNN
}


class EncoderRNN(nn.Module):
    r"""
    Converts low level features into higher level features

    Args:
        in_features (int): size of input
        hidden_size (int): the number of features in the hidden state `h`
        n_layers (int, optional): number of recurrent layers (default: 1)
        bidirectional (bool, optional): if True, becomes a bidirectional encoder (defulat: False)
        rnn_type (str, optional): type of RNN cell (default: gru)
        dropout_p (float, optional): dropout probability for the output sequence (default: 0)

    Inputs: inputs
        - **inputs**: list of sequences, whose length is the batch size and within which each sequence is list of tokens

    Returns: output, hidden
        - **output** (batch, seq_len, hidden_size): tensor containing the encoded features of the input sequence
        - **hidden** (num_layers * num_directions, batch, hidden_size): tensor containing the features in the hidden

    Examples::

        >>> listener = Listener(in_features, hidden_size, dropout_p=0.5, n_layers=5)
        >>> output, hidden = listener(inputs)
    """
    def __init__(self, in_features, hidden_size, dropout_p=0.5, n_layers=5, bidirectional=True, rnn_type='gru'):

        super(EncoderRNN, self).__init__()
        assert rnn_type.lower() in supported_rnns.keys(), 'RNN type not supported.'

        self.rnn_cell = supported_rnns[rnn_type]
        self.embedding = nn.Embedding(in_features, hidden_size)
        self.input_dropout = nn.Dropout(dropout_p)
        self.rnn = self.rnn_cell(
            input_size=hidden_size,
            hidden_size=hidden_size,
            num_layers=n_layers,
            batch_first=True,
            bidirectional=bidirectional,
            dropout=dropout_p
        )

    def forward(self, inputs, input_lengths):
        """ Applies a multi-layer RNN to an input sequence """
        embedded = self.embedding(inputs)
        embedded = self.input_dropout(embedded)

        embedded = nn.utils.rnn.pack_padded_sequence(embedded, input_lengths, batch_first=True)
        output, hidden = self.rnn(embedded)

        output, _ = nn.utils.rnn.pad_packed_sequence(output, batch_first=True)

        return output, hidden
