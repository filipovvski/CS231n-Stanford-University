from builtins import range
from builtins import object
import numpy as np

from cs231n.layers import *
from cs231n.layer_utils import *


def affine_batch_norm_relu_forward(x, w, b, gamma, beta, bn_param, norm, dropout_param):
    cache_bn = None
    cache_ln = None
    cache_drop = None

    out, cache = affine_forward(x, w, b)
    if norm is 'batchnorm':
        out, cache_bn = batchnorm_forward(out, gamma, beta, bn_param)
    if norm is 'layernorm':
        out, cache_ln = layernorm_forward(out, gamma, beta, bn_param)

    out, cache_relu = relu_forward(out)

    if dropout_param:
        out, cache_drop = dropout_forward(out, dropout_param)

    cache = (cache, cache_bn, cache_relu, cache_drop)
    return out, cache


def affine_batch_norm_relu_backwards(dout, cache, norm):
    cache, cache_bn, cache_relu, cache_drop = cache

    if cache_drop:
        dout = dropout_backward(dout, cache_drop)

    dx = relu_backward(dout, cache_relu)

    if norm is 'batchnorm':
        dx, dgamma, dbeta = batchnorm_backward_alt(dx, cache_bn)
    elif norm is 'layernorm':
        dx, dgamma, dbeta = layernorm_backward(dx, cache_bn)

    dx, dw, db = affine_backward(dx, cache)

    return dx, dw, db


class TwoLayerNet(object):
    """
    A two-layer fully-connected neural network with ReLU nonlinearity and
    softmax loss that uses a modular layer design. We assume an input dimension
    of D, a hidden dimension of H, and perform classification over C classes.

    The architecure should be affine - relu - affine - softmax.

    Note that this class does not implement gradient descent; instead, it
    will interact with a separate Solver object that is responsible for running
    optimization.

    The learnable parameters of the model are stored in the dictionary
    self.params that maps parameter names to numpy arrays.
    """

    def __init__(self, input_dim=3 * 32 * 32, hidden_dim=100, num_classes=10,
                 weight_scale=1e-3, reg=0.0):
        """
        Initialize a new network.

        Inputs:
        - input_dim: An integer giving the size of the input
        - hidden_dim: An integer giving the size of the hidden layer
        - num_classes: An integer giving the number of classes to classify
        - weight_scale: Scalar giving the standard deviation for random
          initialization of the weights.
        - reg: Scalar giving L2 regularization strength.
        """
        self.params = {}
        self.reg = reg

        ############################################################################
        # TODO: Initialize the weights and biases of the two-layer net. Weights    #
        # should be initialized from a Gaussian centered at 0.0 with               #
        # standard deviation equal to weight_scale, and biases should be           #
        # initialized to zero. All weights and biases should be stored in the      #
        # dictionary self.params, with first layer weights                         #
        # and biases using the keys 'W1' and 'b1' and second layer                 #
        # weights and biases using the keys 'W2' and 'b2'.                         #
        ############################################################################
        # *****START OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****

        self.params["W1"] = np.random.normal(0, weight_scale, (input_dim, hidden_dim))
        self.params["W2"] = np.random.normal(0, weight_scale, (hidden_dim, num_classes))
        self.params['b1'] = np.zeros(hidden_dim)
        self.params['b2'] = np.zeros(num_classes)

        # *****END OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

    def loss(self, X, y=None):
        """
        Compute loss and gradient for a minibatch of data.

        Inputs:
        - X: Array of input data of shape (N, d_1, ..., d_k)
        - y: Array of labels, of shape (N,). y[i] gives the label for X[i].

        Returns:
        If y is None, then run a test-time forward pass of the model and return:
        - scores: Array of shape (N, C) giving classification scores, where
          scores[i, c] is the classification score for X[i] and class c.

        If y is not None, then run a training-time forward and backward pass and
        return a tuple of:
        - loss: Scalar value giving the loss
        - grads: Dictionary with the same keys as self.params, mapping parameter
          names to gradients of the loss with respect to those parameters.
        """
        scores = None
        ############################################################################
        # TODO: Implement the forward pass for the two-layer net, computing the    #
        # class scores for X and storing them in the scores variable.              #
        ############################################################################

        # *****START OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****

        out, cache_h1 = affine_relu_forward(X, self.params['W1'], self.params['b1'])
        scores, cache_out = affine_forward(out, self.params['W2'], self.params['b2'])

        # *****END OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        # If y is None then we are in test mode so just return scores
        if y is None:
            return scores

        loss, grads = 0, {}
        ############################################################################
        # TODO: Implement the backward pass for the two-layer net. Store the loss  #
        # in the loss variable and gradients in the grads dictionary. Compute data #
        # loss using softmax, and make sure that grads[k] holds the gradients for  #
        # self.params[k]. Don't forget to add L2 regularization!                   #
        #                                                                          #
        # NOTE: To ensure that your implementation matches ours and you pass the   #
        # automated tests, make sure that your L2 regularization includes a factor #
        # of 0.5 to simplify the expression for the gradient.                      #
        ############################################################################
        # *****START OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****

        loss, dx = softmax_loss(scores, y)
        loss += 0.5 * self.reg * (
                np.sum(self.params['W1'] * self.params['W1']) + np.sum(self.params['W2'] * self.params['W2']))

        dx2, dw2, grads['b2'] = affine_backward(dx, cache_out)
        dx2 = dx2.reshape((dx.shape[0], -1))
        dx, dw, grads['b1'] = affine_relu_backward(dx2, cache_h1)

        grads['W2'] = dw2 + self.reg * self.params['W2']
        grads['W1'] = dw + self.reg * self.params['W1']

        # *****END OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        return loss, grads


class FullyConnectedNet(object):
    """
    A fully-connected neural network with an arbitrary number of hidden layers,
    ReLU nonlinearities, and a softmax loss function. This will also implement
    dropout and batch/layer normalization as options. For a network with L layers,
    the architecture will be

    {affine - [batch/layer norm] - relu - [dropout]} x (L - 1) - affine - softmax

    where batch/layer normalization and dropout are optional, and the {...} block is
    repeated L - 1 times.

    Similar to the TwoLayerNet above, learnable parameters are stored in the
    self.params dictionary and will be learned using the Solver class.
    """

    def __init__(self, hidden_dims, input_dim=3 * 32 * 32, num_classes=10,
                 dropout=1, normalization=None, reg=0.0,
                 weight_scale=1e-2, dtype=np.float32, seed=None):
        """
        Initialize a new FullyConnectedNet.

        Inputs:
        - hidden_dims: A list of integers giving the size of each hidden layer.
        - input_dim: An integer giving the size of the input.
        - num_classes: An integer giving the number of classes to classify.
        - dropout: Scalar between 0 and 1 giving dropout strength. If dropout=1 then
          the network should not use dropout at all.
        - normalization: What type of normalization the network should use. Valid values
          are "batchnorm", "layernorm", or None for no normalization (the default).
        - reg: Scalar giving L2 regularization strength.
        - weight_scale: Scalar giving the standard deviation for random
          initialization of the weights.
        - dtype: A numpy datatype object; all computations will be performed using
          this datatype. float32 is faster but less accurate, so you should use
          float64 for numeric gradient checking.
        - seed: If not None, then pass this random seed to the dropout layers. This
          will make the dropout layers deteriminstic so we can gradient check the
          model.
        """
        self.normalization = normalization
        self.use_dropout = dropout != 1
        self.reg = reg
        self.num_layers = 1 + len(hidden_dims)
        self.dtype = dtype
        self.params = {}
        self.parameters = {}

        ############################################################################
        # TODO: Initialize the parameters of the network, storing all values in    #
        # the self.params dictionary. Store weights and biases for the first layer #
        # in W1 and b1; for the second layer use W2 and b2, etc. Weights should be #
        # initialized from a normal distribution centered at 0 with standard       #
        # deviation equal to weight_scale. Biases should be initialized to zero.   #
        #                                                                          #
        # When using batch normalization, store scale and shift parameters for the #
        # first layer in gamma1 and beta1; for the second layer use gamma2 and     #
        # beta2, etc. Scale parameters should be initialized to ones and shift     #
        # parameters should be initialized to zeros.                               #
        ############################################################################
        # *****START OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****

        hidden_dims.insert(0, input_dim)

        for item in range(self.num_layers):
            weight = 'W' + str(item + 1)
            bias = 'b' + str(item + 1)
            gamma = 'gamma' + str(item + 1)
            beta = 'beta' + str(item + 1)

            if item == self.num_layers - 1:
                self.params[weight] = np.random.normal(0, weight_scale, (hidden_dims[item], num_classes))
                self.params[bias] = np.zeros(num_classes)
                continue

            self.parameters[gamma] = np.ones(hidden_dims[item + 1])
            self.parameters[beta] = np.zeros(hidden_dims[item + 1])

            self.params[weight] = np.random.normal(0, weight_scale, (hidden_dims[item], hidden_dims[item + 1]))
            self.params[bias] = np.zeros(hidden_dims[item + 1])

        # *****END OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        # When using dropout we need to pass a dropout_param dictionary to each
        # dropout layer so that the layer knows the dropout probability and the mode
        # (train / test). You can pass the same dropout_param to each dropout layer.
        self.dropout_param = {}
        if self.use_dropout:
            self.dropout_param = {'mode': 'train', 'p': dropout}
            if seed is not None:
                self.dropout_param['seed'] = seed

        # With batch normalization we need to keep track of running means and
        # variances, so we need to pass a special bn_param object to each batch
        # normalization layer. You should pass self.bn_params[0] to the forward pass
        # of the first batch normalization layer, self.bn_params[1] to the forward
        # pass of the second batch normalization layer, etc.
        self.bn_params = []
        if self.normalization == 'batchnorm':
            self.bn_params = [{'mode': 'train'} for i in range(self.num_layers - 1)]
            # print('self.bn_params: ', self.bn_params)
        if self.normalization == 'layernorm':
            self.bn_params = [{} for i in range(self.num_layers - 1)]

        # Cast all parameters to the correct datatype
        # print(self.params.keys())
        for k, v in self.params.items():
            self.params[k] = v.astype(dtype)

    def loss(self, X, y=None):
        """
        Compute loss and gradient for the fully-connected net.

        Input / output: Same as TwoLayerNet above.
        """
        X = X.astype(self.dtype)

        mode = 'test' if y is None else 'train'

        # Set train/test mode for batchnorm params and dropout param since they
        # behave differently during training and testing.
        if self.use_dropout:
            self.dropout_param['mode'] = mode
        if self.normalization == 'batchnorm':
            for bn_param in self.bn_params:
                bn_param['mode'] = mode
        scores = None
        # print(self.bn_params)
        ############################################################################
        # TODO: Implement the forward pass for the fully-connected net, computing  #
        # the class scores for X and storing them in the scores variable.          #
        #                                                                          #
        # When using dropout, you'll need to pass self.dropout_param to each       #
        # dropout forward pass.                                                    #
        #                                                                          #
        # When using batch normalization, you'll need to pass self.bn_params[0] to #
        # the forward pass for the first batch normalization layer, pass           #
        # self.bn_params[1] to the forward pass for the second batch normalization #
        # layer, etc.                                                              #
        ############################################################################
        # *****START OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****

        caches = {}
        layers = []
        outputs = {}

        for number in range(self.num_layers - 1):
            layers.append(('W' + str(number + 2), 'b' + str(number + 2), 'h' +
                           str(number + 2), 'h' + str(number + 1), 'gamma' + str(number + 2),
                           'beta' + str(number + 2), number + 2))

        bn_param = None

        if self.normalization is not None:
            bn_param = self.bn_params[0]

        # print(bn_param.keys())


        outputs['h1'], caches['h1'] = affine_batch_norm_relu_forward(X, self.params['W1'], self.params['b1'],
                                                                     self.parameters['gamma1'],
                                                                     self.parameters['beta1'],
                                                                     bn_param, self.normalization, self.dropout_param)
        # print(layers)
        # print(layers)
        for weights, bias, output, prev, gamma, beta, n in layers:

            # print(weights, bias, output, prev, gamma, beta, n)
            if (weights, bias, output, prev, gamma, beta, n) == layers[-1]:
                scores, caches[str(output)] = affine_forward(outputs[prev], self.params[weights], self.params[bias])
                continue

            bn_param = None
            if self.normalization is not None:
                bn_param = self.bn_params[n - 1]

            outputs[output], caches[str(output)] = affine_batch_norm_relu_forward(outputs[prev],
                                                                                  self.params[weights],
                                                                                  self.params[bias],
                                                                                  self.parameters[gamma],
                                                                                  self.parameters[beta],
                                                                                  bn_param,
                                                                                  self.normalization,self.dropout_param)
        '''
        else:
            for number in range(self.num_layers - 1):
                layers.append(('W' + str(number + 2), 'b' + str(number + 2), 'h' +
                               str(number + 2), 'h' + str(number + 1), 'gamma' + str(number + 2),
                               'beta' + str(number + 2), number + 2, 'r' + str(number + 2)))

            bn_param = self.bn_params[0]

            outputs['h1'], caches['h1'] = layernorm_forward(X, self.parameters['gamma1'], self.parameters['beta1'],
                                                            bn_param)

            outputs['r1'], caches['r1'] = relu_forward(outputs['h1'])
            # print(layers)
            # print(layers)
            for weights, bias, output, prev, gamma, beta, n, r in layers:

                # print(weights, bias, output, prev, gamma, beta, n)
                if (weights, bias, output, prev, gamma, beta, n, r) == layers[-1]:
                    scores, caches[str(output)] = affine_forward(outputs[prev], self.params[weights], self.params[bias])
                    continue

                bn_param = self.bn_params[n - 1]

                outputs[output], caches[str(output)] = layernorm_forward(outputs[prev],
                                                                         self.parameters[gamma],
                                                                         self.parameters[beta],
                                                                         bn_param)

                outputs[output], caches[r] = relu_forward(outputs[output])
            '''
        # *****END OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        # If test mode return early
        if mode == 'test':
            return scores

        loss, grads = 0.0, {}
        ############################################################################
        # TODO: Implement the backward pass for the fully-connected net. Store the #
        # loss in the loss variable and gradients in the grads dictionary. Compute #
        # data loss using softmax, and make sure that grads[k] holds the gradients #
        # for self.params[k]. Don't forget to add L2 regularization!               #
        #                                                                          #
        # When using batch/layer normalization, you don't need to regularize the scale   #
        # and shift parameters.                                                    #
        #                                                                          #
        # NOTE: To ensure that your implementation matches ours and you pass the   #
        # automated tests, make sure that your L2 regularization includes a factor #
        # of 0.5 to simplify the expression for the gradient.                      #
        ############################################################################
        # *****START OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****

        dx = {}
        dw = {}

        layers = []
        for number in range(self.num_layers):
            layers.append(('W' + str(number + 1), 'b' + str(number + 1), 'h' +
                           str(number + 1), 'h' + str(number + 2)))

        layers.reverse()

        loss, dx_out = softmax_loss(scores, y)

        for item in self.params:
            if str(item)[0] == 'W':
                loss += 0.5 * self.reg * (np.sum(self.params[item] * self.params[item]))

        for weights, bias, output, next in layers:
            if (weights, bias, output, next) == layers[0]:
                dx[output], dw[output], grads[bias] = affine_backward(dx_out, caches[output])
                dx[output] = dx[output].reshape((dx_out.shape[0], -1))
                grads[weights] = dw[output] + self.reg * self.params[weights]
                continue

            dx[output], dw[output], grads[bias] = affine_batch_norm_relu_backwards(dx[next], caches[output],
                                                                                   self.normalization)
            dx[output] = dx[output].reshape((dx_out.shape[0], -1))
            grads[weights] = dw[output] + self.reg * self.params[weights]

        '''
        dx3, dw3, grads['b3'] = affine_relu_backward(dx, cache_h3)
        dx3 = dx3.reshape((dx.shape[0], -1))
        dx2, dw2, grads['b2'] = affine_relu_backward(dx3, cache_h2)
        dx2 = dx2.reshape((dx.shape[0], -1))
        dx1, dw1, grads['b1'] = affine_relu_backward(dx2, cache_h1)

        grads['W3'] = dw3 + self.reg * self.params['W3']
        grads['W2'] = dw2 + self.reg * self.params['W2']
        grads['W1'] = dw1 + self.reg * self.params['W1']
        '''
        # *****END OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        return loss, grads
