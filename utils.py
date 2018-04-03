"""
Scipy version > 0.18 is needed, due to 'mode' option from scipy.misc.imread function
"""

import os
import glob
import h5py
import random
import matplotlib.pyplot as plt

from PIL import Image  # for loading images as YCbCr format
import scipy.misc
import scipy.ndimage
import numpy as np

import tensorflow as tf

FLAGS = tf.app.flags.FLAGS

def read_data(path):
  """
  Read h5 format data file
  
  Args:
    path: file path of desired file
    data: '.h5' file format that contains train data values
    label: '.h5' file format that contains train label values
  """
  with h5py.File(path, 'r') as hf:
    data = np.array(hf.get('data'))
    label = np.array(hf.get('label'))
    print("Data opened from: ", path)
    return data, label

def normalization_data_01(data):
    """
    data normalization in 0 till 1 range
    :param data:
    :return:
    """
    if not (len(data.shape)<=3):
        n_imgs = data.shape[0]
        data = np.float32(data)
        if data.shape[-1]==3:
            for i in range(n_imgs):
                # R = data[i,:,:,0]
                img = data[i,:,:,:]
                data[i,:,:,:] = ((img - np.min(img))*1)/(np.max(img)-np.min(img))

        elif data.shape[-1]==4:
            for i in range(n_imgs):
                img = data[i,:,:,:]
                data[i,:,:,:] = ((img - np.min(img))*1)/(np.max(img)-np.min(img))

        elif data.shape[-1]==3 and len(data.shape)==3:
            for i in range(n_imgs):
                # R = data[i,:,:,0]
                # G = data[i,:,:,1]
                # B = data[i,:,:,2]
                data = ((data-np.min(data))*1/(np.max(data)-np.min(data)))
                # data[:,:,0]= ((R-np.min(R))*1/(np.max(R)-np.min(R)))
                # data[:, :, 1] = ((G - np.min(G)) * 1 / (np.max(G) - np.min(G)))
                # data[:, :, 2] = ((B - np.min(B)) * 1 / (np.max(B) - np.min(B)))

        elif data.shape[-1]==2:
            for i in range(n_imgs):
                im = data[i,:,:,0]
                N = data[i,:,:,-1]
                data[i,:,:,0]= ((im-np.min(im))*1/(np.max(im)-np.min(im)))
                data[i, :, :, -1] = ((N - np.min(N)) * 1 / (np.max(N) - np.min(N)))
            del im, N

        elif data.shape[-1]==1 or len(data.shape)==3:
            if not len(data.shape)==3:
                for i in range(n_imgs):
                    img = data[i, :, :, 0]

                    data[i, :, :, 0] = ((img - np.min(img)) * 1 / (np.max(img) - np.min(img)))

                del img
            else:
                for i in range(n_imgs):
                    img = data[i, :, :]

                    data[i, :, :] = ((img - np.min(img)) * 1 / (np.max(img) - np.min(img)))
                print("the sahpe of data is only 3 instead of 4 ", data.shape)
                del img

        print("Data normalized with:", data.shape[-1], "channels")
        return data

    else:
        data = ((data - np.min(data)) * 1 / (np.max(data) - np.min(data)))
        return data

def normalization_data_0255(data):
    """
    data normalization in 0 till 1 range
    :param data:
    :return:
    """
    if not len(data.shape)==2:
        n_imgs = data.shape[0]
        # data = np.float32(data)
        if data.shape[-1]==3 and len(data.shape)==3:
            # for i in range(n_imgs):
                #
                # R = data[i,:,:,0]
                # G = data[i,:,:,1]
                # B = data[i,:,:,2]
                # data[i,:,:,0]= ((R-np.min(R))*255/(np.max(R)-np.min(R)))
                # data[i, :, :, 1] = ((G - np.min(G)) * 255 / (np.max(G) - np.min(G)))
            data = ((data - np.min(data)) * 255 / (np.max(data) - np.min(data)))
            # data = ((data - np.min(data)) * 254 / (np.max(data) - np.min(data)))+1

        elif data.shape[-1]==3 and len(data.shape)==4:
            for i in range(n_imgs):
                # R = data[i,:,:,0]
                # G = data[i,:,:,1]
                # B = data[i,:,:,2]
                # N = data[i,:,:,3]
                # data[i,:,:,0]= ((R-np.min(R))*255/(np.max(R)-np.min(R)))
                # data[i, :, :, 1] = ((G - np.min(G)) * 255 / (np.max(G) - np.min(G)))
                # data[i, :, :, 2] = ((B - np.min(B)) * 255 / (np.max(B) - np.min(B)))
                # data[i, :, :, 3] = ((N - np.min(N)) * 255 / (np.max(N) - np.min(N)))
                img = data[i,...]
                data[i,:,:,:] = ((img - np.min(img)) * 255 / (np.max(img) - np.min(img)))
        # print("Data normalized with:", data.shape[-1], "channels")
        return data

    elif data.shape[-1]==3 and len(data.shape)==3:
        # R = data[:, :, 0]
        # G = data[:, :, 1]
        # B = data[:, :, 2]
        # data[:, :, 0] = ((R-np.min(R))*255/(np.max(R)-np.min(R)))
        # data[:, :, 1] = ((G - np.min(G)) * 255 / (np.max(G) - np.min(G)))
        # data[:, :, 2] = ((B - np.min(B)) * 255 / (np.max(B) - np.min(B)))
        data = ((data - np.min(data)) * 255 / (np.max(data) - np.min(data)))
        return data
    elif len(data.shape)==2:
        data = ((data-np.min(data))*255/(np.max(data)-np.min(data)))
        return data

# save dataset as h5 file
def save_variable_h5(savepath, data):

    with h5py.File(savepath, 'w') as hf:
        hf.create_dataset('data', data=data)

        print("Data [", data.shape, "] saved in: ", savepath)

#  end of my code
# -----------------------------------------------------------------------------------
def preprocess(path, scale=3):
  """
  Preprocess single image file 
    (1) Read original image as YCbCr format (and grayscale as default)
    (2) Normalize
    (3) Apply image file with bicubic interpolation

  Args:
    path: file path of desired file
    input_: image applied bicubic interpolation (low-resolution)
    label_: image with original resolution (high-resolution)
  """
  image = imread(path, is_grayscale=True)
  label_ = modcrop(image, scale)

  # Must be normalized
  image = image / 255.
  label_ = label_ / 255.

  input_ = scipy.ndimage.interpolation.zoom(label_, (1./scale), prefilter=False)
  input_ = scipy.ndimage.interpolation.zoom(input_, (scale/1.), prefilter=False)

  return input_, label_

def prepare_data(sess, dataset):
  """
  Args:
    dataset: choose train dataset or test dataset
    
    For train dataset, output data would be ['.../t1.bmp', '.../t2.bmp', ..., '.../t99.bmp']
  """
  if FLAGS.is_train:
    filenames = os.listdir(dataset)
    data_dir = os.path.join(os.getcwd(), dataset)
    data = glob.glob(os.path.join(data_dir, "*.bmp"))
  else:
    data_dir = os.path.join(os.sep, (os.path.join(os.getcwd(), dataset)), "Set5")
    data = glob.glob(os.path.join(data_dir, "*.bmp"))

  return data

def make_data(sess, data, label):
  """
  Make input data as h5 file format
  Depending on 'is_train' (flag value), savepath would be changed.
  """
  if FLAGS.is_train:
    savepath = os.path.join(os.getcwd(), 'checkpoint/train.h5')
  else:
    savepath = os.path.join(os.getcwd(), 'checkpoint/test.h5')

  with h5py.File(savepath, 'w') as hf:
    hf.create_dataset('data', data=data)
    hf.create_dataset('label', data=label)

def imread(path, is_grayscale=True):
  """
  Read image using its path.
  Default value is gray-scale, and image is read by YCbCr format as the paper said.
  """
  if is_grayscale:
    return scipy.misc.imread(path, flatten=True, mode='YCbCr').astype(np.float)
  else:
    return scipy.misc.imread(path, mode='YCbCr').astype(np.float)

def modcrop(image, scale=3):
  """
  To scale down and up the original image, first thing to do is to have no remainder while scaling operation.
  
  We need to find modulo of height (and width) and scale factor.
  Then, subtract the modulo from height (and width) of original image size.
  There would be no remainder even after scaling operation.
  """
  if len(image.shape) == 3:
    h, w, _ = image.shape
    h = h - np.mod(h, scale)
    w = w - np.mod(w, scale)
    image = image[0:h, 0:w, :]
  else:
    h, w = image.shape
    h = h - np.mod(h, scale)
    w = w - np.mod(w, scale)
    image = image[0:h, 0:w]
  return image

def input_setup(sess, config):
  """
  Read image files and make their sub-images and saved them as a h5 file format.
  """
  # Load data path
  if config.is_train:
    data = prepare_data(sess, dataset="Train")
  else:
    data = prepare_data(sess, dataset="Test")

  sub_input_sequence = []
  sub_label_sequence = []
  padding = abs(config.image_size - config.label_size) / 2 # 6

  if config.is_train:
    for i in range(len(data)):
      input_, label_ = preprocess(data[i], config.scale)

      if len(input_.shape) == 3:
        h, w, _ = input_.shape
      else:
        h, w = input_.shape

      for x in range(0, h-config.image_size+1, config.stride):
        for y in range(0, w-config.image_size+1, config.stride):
          sub_input = input_[x:x+config.image_size, y:y+config.image_size] # [33 x 33]
          sub_label = label_[x+padding:x+padding+config.label_size, y+padding:y+padding+config.label_size] # [21 x 21]

          # Make channel value
          sub_input = sub_input.reshape([config.image_size, config.image_size, 1])  
          sub_label = sub_label.reshape([config.label_size, config.label_size, 1])

          sub_input_sequence.append(sub_input)
          sub_label_sequence.append(sub_label)

  else:
    input_, label_ = preprocess(data[2], config.scale)

    if len(input_.shape) == 3:
      h, w, _ = input_.shape
    else:
      h, w = input_.shape

    # Numbers of sub-images in height and width of image are needed to compute merge operation.
    nx = ny = 0 
    for x in range(0, h-config.image_size+1, config.stride):
      nx += 1; ny = 0
      for y in range(0, w-config.image_size+1, config.stride):
        ny += 1
        sub_input = input_[x:x+config.image_size, y:y+config.image_size] # [33 x 33]
        sub_label = label_[x+padding:x+padding+config.label_size, y+padding:y+padding+config.label_size] # [21 x 21]
        
        sub_input = sub_input.reshape([config.image_size, config.image_size, 1])  
        sub_label = sub_label.reshape([config.label_size, config.label_size, 1])

        sub_input_sequence.append(sub_input)
        sub_label_sequence.append(sub_label)

  """
  len(sub_input_sequence) : the number of sub_input (33 x 33 x ch) in one image
  (sub_input_sequence[0]).shape : (33, 33, 1)
  """
  # Make list to numpy array. With this transform
  arrdata = np.asarray(sub_input_sequence) # [?, 33, 33, 1]
  arrlabel = np.asarray(sub_label_sequence) # [?, 21, 21, 1]

  make_data(sess, arrdata, arrlabel)

  if not config.is_train:
    return nx, ny
    
def imsave(image, path):
  return scipy.misc.imsave(path, image)

def merge(images, size):
  h, w = images.shape[1], images.shape[2]
  img = np.zeros((h*size[0], w*size[1], 1))
  for idx, image in enumerate(images):
    i = idx % size[1]
    j = idx // size[1]
    img[j*h:j*h+h, i*w:i*w+w, :] = image

  return img
