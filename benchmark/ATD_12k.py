import cv2
import math
import sys
import torch
import numpy as np
import argparse
import os
import warnings
from tqdm import tqdm
warnings.filterwarnings('ignore')
torch.set_grad_enabled(False)

'''==========import from our code=========='''
sys.path.append('.')
import config as cfg
from Trainer import Model

parser = argparse.ArgumentParser()
parser.add_argument('--model', default='ours', type=str)
parser.add_argument('--path', type=str, required=True)
args = parser.parse_args()
assert args.model in ['ours', 'ours_small'], 'Model not exists!'


'''==========Model setting=========='''
TTA = True
if args.model == 'ours_small':
    TTA = False
    cfg.MODEL_CONFIG['LOGNAME'] = 'ours_small'
    cfg.MODEL_CONFIG['MODEL_ARCH'] = cfg.init_model_config(
        F = 16,
        depth = [2, 2, 2, 2, 2]
    )
else:
    cfg.MODEL_CONFIG['LOGNAME'] = 'ours'
    cfg.MODEL_CONFIG['MODEL_ARCH'] = cfg.init_model_config(
        F = 32,
        depth = [2, 2, 2, 4, 4]
    )
model = Model(-1)
model.load_model()
model.eval()
model.device()


print(f'=========================Starting testing=========================')
print(f'Dataset: ATD  Model: {model.name}   TTA: {TTA}')
path = args.path
f = os.listdir(os.path.join(path, 'test_2k_540p'))
psnr_list, ssim_list = [], []
for i in f:
    name = str(i).strip()
    size = (384, 192)
    if(len(name) <= 1):
        continue
    I0 = cv2.imread(path + '/test_2k_540p/' + name + '/frame1.jpg')
    I1 = cv2.imread(path + '/test_2k_540p/' + name + '/frame2.jpg')
    I2 = cv2.imread(path + '/test_2k_540p/' + name + '/frame3.jpg') # BGR -> RBG
    I0 = cv2.resize(I0, size)
    I1 = cv2.resize(I1, size)
    I2 = cv2.resize(I2, size)
    I0 = (torch.tensor(I0.transpose(2, 0, 1)).cuda() / 255.).unsqueeze(0)
    I2 = (torch.tensor(I2.transpose(2, 0, 1)).cuda() / 255.).unsqueeze(0)
    mid = model.inference(I0, I2, TTA=TTA, fast_TTA=TTA)[0]
    # ssim = ssim_matlab(torch.tensor(I1.transpose(2, 0, 1)).cuda().unsqueeze(0) / 255., mid.unsqueeze(0)).detach().cpu().numpy()
    mid = mid.detach().cpu().numpy().transpose(1, 2, 0)
    I1 = I1 / 255.
    psnr = -10 * math.log10(((I1 - mid) * (I1 - mid)).mean())
    os.makedirs('/home/curry/jshe2377/emavfi/' + name)
    mid = mid * 255.
    cv2.imwrite(r"/home/curry/jshe2377/emavfi/"+name+"/emavfi.png", mid)
    psnr_list.append(psnr)
    # ssim_list.append(ssim)


    print("Avg PSNR: {} SSIM: {}".format(np.mean(psnr_list), np.mean(ssim_list)))
