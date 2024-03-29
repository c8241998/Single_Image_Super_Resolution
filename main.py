# the main entrance of the training pipeline

from dataset import data
import os
from utils import *
from model import MyModel
import datetime
os.environ["CUDA_VISIBLE_DEVICES"]="0,7,6,5,4,3,2,1"

if __name__=='__main__':

    # parameters
    config = read_config()
    scale = int(config['dataset'][-1:])
    checkpoint_path = 'checkpoint/' + config['dataset'][-10:] + '/model'
    log_dir = "logs/fit/" + config['dataset'] + '-' + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    # dataset
    trainset,valset,testset = data(name=config['dataset'])

    # model
    model = MyModel(blocks=config['blocks'],channel=config['channel'],scale=scale)

    # lr ExponentialDecay
    lr_schedule = tf.keras.optimizers.schedules.ExponentialDecay(config['learning_rate'],
                                                                 decay_steps=config['decay_steps'],
                                                                 decay_rate=config['decay_rate'])

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=lr_schedule),
        loss= Loss(),
        metrics=[PSNR(),SSIM()],
    )

    # resume checkpoint
    if config['resume']:
        model.build((None,None,None,3))
        model.load_weights(checkpoint_path)

    # save the best model checkpoint
    model_checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
        filepath=checkpoint_path,
        save_weights_only=True,
        monitor='val_loss',
        mode='min',
        save_best_only=True)

    # tensorboard visulization
    tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir, histogram_freq=1)

    # model fit
    model.fit(
        trainset,
        epochs=config['epochs'],
        validation_data=valset,
        validation_freq=1,
        callbacks = [model_checkpoint_callback,tensorboard_callback]
    )

    # model summary
    print(model.summary())