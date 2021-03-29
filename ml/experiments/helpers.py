import numpy as np
import torch
import matplotlib as mpl
import cv2
import pysift
from math import sin, cos, sqrt, atan2, radians

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

def generate_points(img, x0, y0, dx, dy, step, window_size, nan_val=-100):  
    points = []
    for x in range(x0+window_size[1]//2, x0+dx-window_size[1]//2, step):
        for y in range(y0+window_size[0]//2, y0+dy-window_size[0]//2, step):
            if img[y, x] != nan_val:
                points.append([y, x])
    return points

def colorFader(c1, c2, mix=0): #fade (linear interpolate) from color c1 (at mix=0) to c2 (mix=1)
    assert mix >= 0 and mix <= 1
    c1=np.array(mpl.colors.to_rgb(c1))
    c2=np.array(mpl.colors.to_rgb(c2))
    return mpl.colors.to_hex((1-mix)*c1 + mix*c2)

#   latitude - y
#   longitude - x
def calculate_distance(metadata, xy1, xy2):
    R = 6373.0
    lat_res = metadata['b0_proj_common']['latRes']
    lon_res = metadata['b0_proj_common']['lonRes']
    
    lat1 = radians(xy1[0]*lat_res/3600)
    lon1 = radians(xy1[1]*lon_res/3600)
    lat2 = radians(xy2[0]*lat_res/3600)
    lon2 = radians(xy2[1]*lon_res/3600)
    
    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c * 1000
    return distance
    

def ssim(x, y, coefs):
    if coefs is None:
        alpha = 1
        beta = 1
        gamma = 1
    else:
        alpha = coefs['alpha']
        beta = coefs['beta']
        gamma = coefs['gamma']
    
    x = x.reshape(1, -1)
    x_mean = torch.mean(x, 1)
    y_mean = torch.mean(y, 1)
    x_diff = x - x_mean.view(-1, 1)
    y_diff = y - y_mean.view(-1, 1)
    x_std = torch.std(x, 1)
    y_std = torch.std(y, 1)

    C = torch.sum(x_diff*y_diff, 1) / torch.sqrt(torch.sum(torch.pow(x_diff,2), 1)*torch.sum(torch.pow(y_diff,2), 1))
    E = 1 - torch.sum(torch.abs(x_diff - y_diff), 1) / (torch.sum(torch.abs(x_diff), 1) + torch.sum(torch.abs(y_diff), 1))
    S = 2*x_std*y_std/(torch.pow(x_std,2) + torch.pow(y_std,2))
    
    ssim = (C**alpha * E**beta * S**gamma).cpu()
    return ssim

def rmse(x, y, coefs):
    x = x.reshape(1, -1)
    score = torch.sqrt(torch.mean(torch.pow(x-y, 2), 1))
    return score

def prepare_ref_img(img, point_coor, window_size):
    ref_window_lcx = point_coor[1]-window_size[1]//2
    ref_window_rcx = ref_window_lcx+window_size[1]
    ref_window_ucy = point_coor[0]-window_size[0]//2
    ref_window_dcy = ref_window_ucy+window_size[0]
    
    return img[ref_window_ucy:ref_window_dcy, ref_window_lcx:ref_window_rcx]

def find_best_match(img1,  # image where we gotta find our point
                    img2,  # image where we pined point
                    point_coor, 
                    window_size, 
                    vicinity_size, 
                    metric_fn, # metric function wanna maximize: metric_fn(crop1, crop2, coefs)
                    device,
                    mode='max',
                    coefs=None): # coeficients for metric_fn
    
    assert mode in ['max', 'min']

    ref_image = prepare_ref_img(img1, point_coor, window_size)
    vicinity_lcx = point_coor[1]-vicinity_size[1]//2
    vicinity_rcx = vicinity_lcx+vicinity_size[1]
    
    # BADTRIP HANDLER 1
    if vicinity_lcx < 0:
        vicinity_lcx = 0
        vicinity_rcx = vicinity_size[1]
    # BADTRIP HANDLER 2
    if vicinity_rcx >= img2.shape[1]:
        vicinity_rcx = img2.shape[1]-1
        vicinity_lcx = vicinity_rcx - vicinity_size[1]
        if vicinity_lcx < 0:
            vicinity_lcx = 0
    
    vicinity_ucy = point_coor[0]-vicinity_size[0]//2
    vicinity_dcy = vicinity_ucy+vicinity_size[0]
    
    # BADTRIP HANDLER 3
    if vicinity_ucy < 0:
        vicinity_ucy = 0
        vicinity_dcy = vicinity_size[0]
    # BADTRIP HANDLER 4
    if vicinity_dcy >= img2.shape[0]:
        vicinity_dcy = img2.shape[0]-1
        vicinity_ucy = vicinity_dcy - vicinity_size[0]
        if vicinity_dcy < 0:
            vicinity_dcy = 0
        
    idx = []
    yx = []
    imgs = torch.zeros((
        (vicinity_dcy-vicinity_ucy-window_size[0])*(vicinity_rcx-vicinity_lcx-window_size[1]),
        window_size[1]*window_size[0]
    )).to(device)
    
    c = 0
  
    for y in range(vicinity_ucy, vicinity_dcy-window_size[0]):
        for x in range(vicinity_lcx, vicinity_rcx-window_size[1]):
            idx.append([(2*y + window_size[0])//2, (2*x + window_size[1])//2])
            yx.append([y, x])
            img2_crop = img2[y:y+window_size[0], x:x+window_size[1]]
            imgs[c] = img2_crop.reshape(-1)
            c += 1
    
    scores = metric_fn(ref_image, imgs, coefs)
    if mode == 'max':
        l = torch.argmax(scores).item()
        return idx[l], scores[l].item(), imgs[l].cpu().view(window_size[0], window_size[1]), yx[l]
    else:
        l = torch.argmin(scores).item()
        return idx[l], scores[l].item(), imgs[l].cpu().view(window_size[0], window_size[1]), yx[l]

def find_best_in_vicinity(vicinity, ref_image, yx_global, 
                    window_size, metric_fn, # metric function wanna maximize: metric_fn(crop1, crop2, coefs)
                    device, mode='max', coefs=None):
    
    assert mode in ['max', 'min']
    assert vicinity.shape[0] > window_size[0]
    assert vicinity.shape[1] > window_size[1]
    
    idx = []
    yx = []
    imgs = torch.zeros((
        (vicinity.shape[0]-window_size[0])*(vicinity.shape[1]-window_size[1]),
        window_size[1]*window_size[0]
    )).to(device)
    
    c = 0
  
    for y in range(vicinity.shape[0]-window_size[0]):
        for x in range(vicinity.shape[1]-window_size[1]):
            tmp_y = y + yx_global[0]
            tmp_x = x + yx_global[1]
            idx.append([(2*tmp_y + window_size[0])//2, (2*tmp_x + window_size[1])//2])
            yx.append([tmp_y, tmp_x])
            img2_crop = vicinity[y:y+window_size[0], x:x+window_size[1]]
            imgs[c] = img2_crop.reshape(-1)
            c += 1
    
    scores = metric_fn(ref_image, imgs, coefs)
    if mode == 'max':
        l = torch.argmax(scores).item()
        return idx[l], scores[l].item(), imgs[l].cpu().view(window_size[0], window_size[1]), yx[l]
    else:
        l = torch.argmin(scores).item()
        return idx[l], scores[l].item(), imgs[l].cpu().view(window_size[0], window_size[1]), yx[l]
    
if __name__ == '__main__':
    device = 'cpu'
    
    b0, data1 = parse('20060504_072852_NOAA_12.m.pro')
    data1[data1 < 0] = 0
    data1 = data1.astype(np.uint8)
    
    b0, data2 = parse('20060504_125118_NOAA_17.m.pro')
    data2[data2 < 0] = 0
    data2 = data2.astype(np.uint8)
    
    surf = cv2.SIFT_create()
    
    kp1, des1 = surf.detectAndCompute(data1, None)
    kp2, des2 = surf.detectAndCompute(data2, None)
    print(kp1)
    print(des1)
    # create BFMatcher object
    bf = cv2.BFMatcher(2, crossCheck=False)
    # Match descriptors.
    matches = bf.match(des1,des2)
    matches = sorted(matches, key = lambda x:x.distance) 
    
    print('Hi', matches)