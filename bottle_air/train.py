import os
from hyperopt import fmin, tpe, hp, STATUS_OK, Trials, space_eval
from keras.callbacks import ModelCheckpoint

def info(title):
    """ Prints out some threads stats. """
    print title
    print 'module name: ' +  __name__
    print 'parent process: ' + str(os.getppid())
    print 'process id: ' + str(os.getpid())
['relu', 'sigmoid', 'tanh', 'linear']

def gen_layer(num_ls, num_l, width):
  """ Given the number of layers, the layer number and width, returns a choice of activation for the layer. """
  return (width, hp.choice('layer activation ' + str(num_ls) + str(num_l) + str(width), ['relu', 'sigmoid', 'tanh', 'linear']))

def layer_choice(num):
  """ Given the number of layers, returns a choice of differing width and activations layers. """
  layer_neurons = []
  for i in range(num):
    # Choose number of neurons from 1 - 10.
    layer_neurons.append(hp.choice('num_layers ' + str(num) + ' layer ' + str(i), [('num_layers ' + str(num) + ' layer ' + str(i) + ' width ' + str(x), gen_layer(num, i, x)) for x in range(1,11)]))
  return layer_neurons

def train(handle, train_epochs=20):
  """ Runs TPE black box optimization of the neural network to use.
  After evaluating all points, it saves the best model to disk and sets the status flag as TRAINED.
  """
  from db import get_model, save_model
  from model import ModelStatus
  info('Running training on new process')
  air_model = get_model(handle)
  air_model.status = ModelStatus.TRAINING
  save_model(air_model)
  
  fspace = {
    'optimizer': hp.choice('optimzer', ['rmsprop', 'adagrad']),
    'layers': hp.choice('layers', [(str(x), layer_choice(x)) for x in range(10)])  # Choose from 0 to 9 layers.
  }

  trials = Trials()
  best = fmin(fn=air_model.run_model(), space=fspace, algo=tpe.suggest, max_evals=train_epochs, trials=trials)

  print 'best:', space_eval(fspace, best)

  print 'trials:'
  for trial in trials.trials[:2]:
      print trial
  
  model_fn = air_model.run_model(persist=True)
  model_fn(space_eval(fspace, best))  # Train and persist best model.

  print 'Training finished'
  air_model.status = ModelStatus.TRAINED
  air_model.best_model = best
  save_model(air_model)
