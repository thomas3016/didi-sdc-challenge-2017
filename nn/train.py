"""
train.py

Train the neural network to predict location and orientation of obstacles

Example:
    python train.py --data_dir=/vol/dataset2/Didi-Release-2/Tracklets/1pc/15pc/


"""

# TODO: This will evolve over time to handle more than 1 bag, to become a ROS subscriber, etc.
# TODO: Need to predict obstacle l,w,h
# TODO: Train to recognise more than one obstacle

import os
import nn
import argparse
import numpy as np
from data_reader import DataReader
#TODO: Put these into nn.py
from keras.callbacks import Callback, TensorBoard, EarlyStopping, ModelCheckpoint

# TODO: Remove what's not needed here
#BATCH_SIZE = 32
BATCH_SIZE = 2
VAL_BATCH_SIZE = 32
#DATA_DIR = '/vol/didi/dataset2/Tracklets/1/2/'
DATA_DIR = '/vol/dataset2/Didi-Release-2/Tracklets/'
LOGDIR = '/vol/training/logs'
TRAIN_DIR = '/vol/dataset2/Didi-Release-2/Train/'
BAG_CSV = 'data/training_data.csv'        # TODO - add back into args
CHECKPOINT_EVERY = 100
NUM_STEPS = int(1e2)   # Run for 100 steps
CKPT_FILE = 'model.ckpt'
LEARNING_RATE = 1e-3
KEEP_PROB = 0.8
L2_REG = 0
EPSILON = 0.001
MOMENTUM = 0.9


def get_arguments():
    parser = argparse.ArgumentParser(description='Udacity Challenge Training')
    parser.add_argument('--batch_size', type=int, default=BATCH_SIZE,
                        action='store', dest='batch_size', help='Number of [camera] samples in batch.')
    parser.add_argument('--data_dir', '--data', type=str, default=DATA_DIR,
                        action='store', dest='data_dir', help='The directory containing the training data.')
    # parser.add_argument('--data_csv', '--csv', type=str, default=BAG_CSV,
    #                     action='store', dest='csv', help='The csv containing the training data.')
    parser.add_argument('--logdir', type=str, default=LOGDIR,
                        help='Directory for log files.')
    parser.add_argument('--restore_from', type=str, default=None,
                        help='Checkpoint file to restore model weights from.')
    parser.add_argument('--checkpoint_every', type=int, default=CHECKPOINT_EVERY,
                        help='How many steps to save each checkpoint after')
    parser.add_argument('--num_steps', type=int, default=NUM_STEPS,
                        help='Number of training steps.')
    parser.add_argument('--learning_rate', type=float, default=LEARNING_RATE,
                        help='Learning rate for training.')
    parser.add_argument('--keep_prob', type=float, default=KEEP_PROB,
                        help='Dropout keep probability.')
    parser.add_argument('--l2_reg', type=float,
                        default=L2_REG)
    return parser.parse_args()

# def save_train_batch(i, xs, ys):
#     xs_filename = os.path.join(TRAIN_DIR, str(i) + '_xs.npy')
#     ys_filename = os.path.join(TRAIN_DIR, str(i) + '_ys.npy')
#     np.save(xs_filename, xs)
#     np.save(ys_filename, ys)

def main():
    args=get_arguments()

    start_step = 0
    LossHistory, model = nn.top_nn()
    #summary = model.summary()
    #print (summary)     # TODO: Write to disk together with diagram (see keras.model_to_dot)

    #TODO: Put these into nn.py and parameterise
    early_stop = EarlyStopping(monitor='val_loss', min_delta=0.001, patience=10, mode='min', verbose=1)
    checkpoint = ModelCheckpoint('weights.hdf5', monitor='val_loss', verbose=1, save_best_only=True, mode='min',
                                 period=1)
    tensorboard = TensorBoard(log_dir='../logs/', histogram_freq=0, write_graph=True, write_images=False)

    data_reader = DataReader(BAG_CSV, DATA_DIR)

    #FIXME: Based on number of steps, convert to number of epochs
    for i in range(start_step, start_step + args.num_steps):
        xs, ys = data_reader.load_train_batch(batch_size=args.batch_size)

        train_error = model.train_on_batch(xs, ys) #, callbacks = [early_stop, checkpoint, tensorboard])
        print ('{}/{}: Training loss: {}'.format(i, start_step + args.num_steps, train_error))

        if i % 10 == 0:
            xs, ys = data_reader.load_val_batch(batch_size=VAL_BATCH_SIZE)
            val_error = model.test_on_batch(xs, ys)
            print ('{}/{}: Validation loss: {}'.format(i, start_step + args.num_steps, val_error))

            if i > 0 and i % args.checkpoint_every == 0:
                if not os.path.exists(args.logdir):
                    os.makedirs(args.logdir)
                filename = 'model-step-%d-val-%g.ckpt' % (i, val_error[1])
                checkpoint_path = os.path.join(args.logdir, filename)
                model.save(checkpoint_path)
                print('Model saved in file: {}'.format(filename))

            # TODO - Add in exit if vol_loss < min_loss

            # TODO - Write logs (if we can in Keras!)

            # TODO - Write loss history and other metrics for graphing...

    # Training has finished
    filename = 'model-final-step-%d-val-%g.ckpt' % (i, val_error[1])
    checkpoint_path = os.path.join(args.logdir, filename)
    model.save_weights(checkpoint_path)
    print ('Final model saved as {}', filename)

if __name__ == '__main__':
    main()





