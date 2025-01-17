from builtins import range
import numpy as np
from random import shuffle
from past.builtins import xrange

def softmax_loss_naive(W, X, y, reg):
    """
    Softmax loss function, naive implementation (with loops)

    Inputs have dimension D, there are C classes, and we operate on minibatches
    of N examples.

    Inputs:
    - W: A numpy array of shape (D, C) containing weights.
    - X: A numpy array of shape (N, D) containing a minibatch of data.
    - y: A numpy array of shape (N,) containing training labels; y[i] = c means
      that X[i] has label c, where 0 <= c < C.
    - reg: (float) regularization strength

    Returns a tuple of:
    - loss as single float
    - gradient with respect to weights W; an array of same shape as W
    """
    # Initialize the loss and gradient to zero.
    loss = 0.0
    dW = np.zeros_like(W)

    #############################################################################
    # TODO: Compute the softmax loss and its gradient using explicit loops.     #
    # Store the loss in loss and the gradient in dW. If you are not careful     #
    # here, it is easy to run into numeric instability. Don't forget the        #
    # regularization!                                                           #
    #############################################################################
    # *****START OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****

    scores = X.dot(W)
    num_train = X.shape[0]
    num_classes = W.shape[1]

    # Softmax Loss
    for i in range(num_train):
        f = scores[i] - np.max(scores[i])  # avoid numerical instability
        softmax = np.exp(f) / np.sum(np.exp(f))
        loss += -np.log(softmax[y[i]])
        # Weight Gradients
        for j in range(num_classes):
            dW[:, j] += X[i] * softmax[j]
        dW[:, y[i]] -= X[i]





    # Average
    loss /= num_train
    dW /= num_train

    # Regularization
    loss += reg * np.sum(W * W)
    dW += reg * 2 * W


    # *****END OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****

    return loss, dW


def softmax_loss_vectorized(W, X, y, reg):
    """
    Softmax loss function, vectorized version.

    Inputs and outputs are the same as softmax_loss_naive.
    """
    # Initialize the loss and gradient to zero.
    loss = 0.0
    dW = np.zeros_like(W)

    #############################################################################
    # TODO: Compute the softmax loss and its gradient using no explicit loops.  #
    # Store the loss in loss and the gradient in dW. If you are not careful     #
    # here, it is easy to run into numeric instability. Don't forget the        #
    # regularization!                                                           #
    #############################################################################
    # *****START OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****

    scores = X.dot(W)
    num_train = X.shape[0]
    num_classes = W.shape[1]

    maxes = np.reshape(np.max(scores, axis=1), (-1, 1))
    multi = maxes.dot(np.ones([1, scores.shape[1]]))
    f = scores - multi

    sum = np.sum(np.exp(f), axis=1)
    sum = np.reshape(sum, (-1, 1))

    softmax = np.divide(np.exp(f), sum)
    #print(softmax.shape, X.shape)

    k = np.reshape(np.arange(num_train), (-1, 1))
    softmax_good_class = softmax[k, y[k]]

    #softmax_good_class = softmax[np.arange(num_train), y]
    softmax_good_class = np.reshape(softmax_good_class, (X.shape[0], ))

    loss = -np.log(softmax_good_class)
    loss = np.sum(loss)

    softmax[k, y[k]] -= 1
    #softmax[np.arange(num_train), y] -= 1
    dW = X.T.dot(softmax)


    #print(dW.shape)

    dW /= num_train
    # Average
    loss /= num_train

    # Regularization
    loss += reg * np.sum(W * W)
    dW += reg * 2 * W
    #print(y)
    #print(softmax[k, y[k]].shape)
    #print(softmax[3])


    # *****END OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****

    return loss, dW
