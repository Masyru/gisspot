import numpy as np
import torch

b0_common_dt = np.dtype([
    ("formatType", np.uint8),
    ("satName", "S13"),
    ("satId", np.uint32),
    ("revNum", np.uint32),
    ("year", np.uint16),
    ("day", np.uint16),
    ("dayTime", np.uint32),
    ("o_year", np.uint16),
    ("o_day", np.uint16),
    ("o_time", np.uint32),
    ("reserved", (np.uint8, 23)),
    ("receiver", np.uint8),
    ("dataType1", np.uint8),
    ("dataType2", np.uint8),
])

b0_proj_common_dt = np.dtype([
    ("processLevel", np.uint32),
    ("channel", np.uint16),
    ("maxPixelValue", np.uint16),
    ("projType", np.uint16),
    ("scanNum", np.uint16),
    ("pixNum", np.uint16),
    ("lat", np.float32),
    ("lon", np.float32),
    ("latSize", np.float32),
    ("lonSize", np.float32),
    ("latRes", np.float32),
    ("lonRes", np.float32),
])

# NORAD
b0_norad_dt = np.dtype([
    ("NORADrevNum", np.uint32),
    ("setNum", np.uint16),
    ("ephemType", np.uint16),
    ("NORADyear", np.uint16),
    ("yearTime", np.float64),
    ("n0", np.float64),
    ("bstar", np.float64),
    ("i0", np.float64),
    ("raan", np.float64),
    ("e0", np.float64),
    ("w0", np.float64),
    ("m0", np.float64),
    ("dataName", "S32"),
    ("dataUnitsName", "S22"),
])

# Corparams
b0_corparams_dt = np.dtype([
    ("corVersion", np.uint16),
    ("orbitModelType", np.uint16),
    ("corTime", np.int16),
    ("corRoll", np.float64),
    ("corPitch", np.float64),
    ("corYaw", np.float64),
    ("gravitModel", np.uint16),
    ("spare", (np.uint8, 512 - 288)),
])

# Types

# Projection
b0_proj_dt = np.dtype([
    # common
    ("b0_common", b0_common_dt),
    # proj_common
    ("b0_proj_common", b0_proj_common_dt),
    # proj_specific
    ("ka", np.float64),
    ("kb", np.float64),
    ("channelName", "S10"),
    # NORAD
    ("b0_norad", b0_norad_dt),
    # CorParams
    ("b0_corparams", b0_corparams_dt),
])

# DOTC
b0_dotc_dt = np.dtype([
    # common
    ("b0_common", b0_common_dt),
    # proj_common
    ("b0_proj_common", b0_proj_common_dt),
    # dotc_specific
    ("algo", np.uint16),
    ("nsect", np.uint16),
    ("win_grad", np.uint16),
    ("win_ever", np.uint16),
    ("step_x", np.uint16),
    ("step_y", np.uint16),
    ("step_grad", np.uint16),
    ("step_ever", np.uint16),
    ("signif", np.uint16),
    ("reserved1", (np.uint8, 8)),
    # NORAD
    ("b0_norad", b0_norad_dt),
    # CorParams
    ("b0_corparams", b0_corparams_dt),
])

def parse(fname):
    f = open(fname, 'rb')
    b0 = np.fromfile(f, dtype=b0_proj_dt, count=1)
    sizeX = b0['b0_proj_common']['pixNum'][0]
    sizeY = b0['b0_proj_common']['scanNum'][0]
    data = np.fromfile(f, dtype='int16')
    data = data.reshape(sizeY, sizeX)
    data = np.flipud(data)
    f.close()
    return b0, data

def convert_image(b0, data):
    mask = data[data<0]
    data = b0['ka']*data + b0['kb']
    data[mask] = np.nan
    return data

def normalize(data):
    data = data/data.max()
    data[data < 0] = np.nan
    return data

def rmse(data1, data2, coefs):
    data1 = data1[~np.isnan(data1)].reshape(-1)
    data2 = data2[~np.isnan(data2)].reshape(-1)
    return np.sqrt(((data1-data2)**2).sum()/data1.shape[0])

def ssim(x, y, coefs):
    if coefs is None:
        alpha = 1
        beta = 1
        gamma = 1
    else:
        alpha = coefs['alpha']
        beta = coefs['beta']
        gamma = coefs['gamma']
    
    x = x.reshape(-1)
    y = y.reshape(-1)
    x = x[~np.isnan(x)]
    y = y[~np.isnan(x)]
    
    x_mean = np.mean(x)
    y_mean = np.mean(y)
    x_diff = x - x_mean
    y_diff = y - y_mean
    x_std = np.std(x)
    y_std = np.std(y)

    C = np.sum(x_diff*y_diff) / np.sqrt(np.sum(np.power(x_diff,2))*np.sum(np.power(y_diff,2)))
    E = 1 - np.sum(np.abs(x_diff - y_diff)) / (np.sum(np.abs(x_diff)) + np.sum(np.abs(y_diff)))
    S = 2*x_std*y_std/ (np.power(x_std,2) + np.power(y_std,2))
    
    ssim = C**alpha * E**beta * S**gamma
    return ssim
    

def mode_comp(a, b, mode):
    return max(a, b) if mode == 'max' else min(a, b)

def find_best_match(img1,  # image where we gotta find our point
                    img2,  # image where we pined point
                    point_coor, 
                    window_size, 
                    vicinity_size, 
                    metric_fn, # metric function wanna maximize: metric_fn(crop1, crop2, coefs)
                    mode='max',
                    coefs=None): # coeficients for metric_fn
    
    assert mode in ['max', 'min']
    
    ref_window_lcx = point_coor[1]-window_size[1]//2
    ref_window_rcx = ref_window_lcx+window_size[1]
    ref_window_ucy = point_coor[0]-window_size[0]//2
    ref_window_dcy = ref_window_ucy+window_size[0]
    
    vicinity_lcx = point_coor[1]-vicinity_size[1]//2
    vicinity_rcx = vicinity_lcx+vicinity_size[1]
    vicinity_ucy = point_coor[0]-vicinity_size[0]//2
    vicinity_dcy = vicinity_ucy+vicinity_size[0]
    
    ref_image = img1[ref_window_ucy:ref_window_dcy, ref_window_lcx:ref_window_rcx]
    
    best_score = -float('infinity') if mode == 'max' else float('infinity')
    best_idx = [None, None]
    for y in range(vicinity_ucy, vicinity_dcy-window_size[0]):
        for x in range(vicinity_lcx, vicinity_rcx-window_size[1]):
            img2_crop = img2[y:y+window_size[0], x:x+window_size[1]]
            score = metric_fn(ref_image, img2_crop, coefs)
            tmp = mode_comp(score, best_score, mode)
            if tmp == score:
                best_score = score
                best_idx[0] = (2*y + window_size[0])//2
                best_idx[1] = (2*x + window_size[1])//2
    
    return best_idx, best_score


def find_best_match_cuda(img1,  # image where we gotta find our point
                    img2,  # image where we pined point
                    point_coor, 
                    window_size, 
                    vicinity_size, 
                    metric_fn, # metric function wanna maximize: metric_fn(crop1, crop2, coefs)
                    mode='max',
                    coefs=None): # coeficients for metric_fn
    
    assert mode in ['max', 'min']
    
    ref_window_lcx = point_coor[1]-window_size[1]//2
    ref_window_rcx = ref_window_lcx+window_size[1]
    ref_window_ucy = point_coor[0]-window_size[0]//2
    ref_window_dcy = ref_window_ucy+window_size[0]
    
    vicinity_lcx = point_coor[1]-vicinity_size[1]//2
    vicinity_rcx = vicinity_lcx+vicinity_size[1]
    vicinity_ucy = point_coor[0]-vicinity_size[0]//2
    vicinity_dcy = vicinity_ucy+vicinity_size[0]
    
    ref_image = img1[ref_window_ucy:ref_window_dcy, ref_window_lcx:ref_window_rcx].reshape(-1)
    
    best_score = -float('infinity') if mode == 'max' else float('infinity')
    best_idx = [None, None]
    
    idx = []
    imgs = torch.empty((
        (vicinity_dcy-window_size[0]-vicinity_ucy)*(vicinity_rcx-window_size[1]-vicinity_lcx)+1,
        window_size[1]*window_size[0]))
    c = 0
    for y in range(vicinity_ucy, vicinity_dcy-window_size[0]):
        for x in range(vicinity_lcx, vicinity_rcx-window_size[1]):
            c += 1
            idx.append([(2*y + window_size[0])//2, (2*x + window_size[1])//2])
            img2_crop = img2[y:y+window_size[0], x:x+window_size[1]]
            imgs[c] = img2_crop.reshape(-1)
    
    imgs = imgs.cuda()
    
    return metric_fn(ref_image, imgs, coefs)


def ssim_cuda(x, y, coefs):
    if coefs is None:
        alpha = 1
        beta = 1
        gamma = 1
    else:
        alpha = coefs['alpha']
        beta = coefs['beta']
        gamma = coefs['gamma']
    
    
    x_mean = torch.mean(x)
    y_mean = torch.mean(y, 1)
    x_diff = x - x_mean
    y_diff = y - y_mean.view(-1, 1)
    x_std = torch.std(x)
    y_std = torch.std(y, 1)
    x = x.reshape(1, -1)
    
    print(x.size(), y.size(), x_mean.size(), y_mean.size(), x_diff.size(), y_diff.size(), x_std.size(), y_std.size())
    
    C = torch.sum(x_diff*y_diff, 1) / torch.sqrt(torch.sum(torch.pow(x_diff,2), 1)*torch.sum(torch.pow(y_diff,2), 1))
    E = 1 - torch.sum(torch.abs(y_diff-x_diff), 1) / (torch.sum(torch.abs(x_diff), 1) + torch.sum(torch.abs(y_diff), 1))
    S = 2*x_std*y_std/ (torch.pow(x_std,2) + torch.pow(y_std,2))
    
    ssim = (C**alpha * E**beta * S**gamma).cpu()
    return ssim