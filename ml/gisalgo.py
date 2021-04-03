import numpy as np
import torch
from math import sin, cos, sqrt, atan2, radians
from typing import List, Tuple, Callable
import sys
sys.path.append("../")
import ml.projmapper as pm

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

# Data Types
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

# .pro files parsing
# Return metadata and image
def parse(f) -> Tuple:
    if type(f) is str:
        f = open(f, 'rb')

    b0 = np.fromfile(f, dtype=b0_proj_dt, count=1)
    sizeX = b0['b0_proj_common']['pixNum'][0]
    sizeY = b0['b0_proj_common']['scanNum'][0]
    data = np.fromfile(f, dtype='int16')
    data = data.reshape(sizeY, sizeX)
    data = np.flipud(data)
    f.close()
    return b0, data

# Convert numpy images to torch and fill NaN
# Return (torch.FloatTensor, torch.FloatTensor)
def numpy2torch(img1: np.float32, img2: np.float32) -> Tuple[torch.FloatTensor]:

    '''
    Vars:
        img1 - first image
        img2 - second image
    '''

    img1 = img1.astype(float)
    img1[img1 < 0] = -100

    img2 = img2.astype(float)
    img2[img2 < 0] = -100
    return torch.tensor(img1, dtype=torch.float32), torch.tensor(img2, dtype=torch.float32)

# Note:
# latitude - y
# longitude - x

# Calculate distance between two points
# Return distance in meters
def calculate_distance(metadata: b0_proj_dt, xy1: Tuple[float],
                       xy2: Tuple[float], tpe: str = 'geo') -> float:

    '''
    Vars:
        metadata - metadata
        xy1 - coordinates of the first point (y, x)
        xy2 - coordinates of the second point (y, x)
        tpe - coordinates type:
            -- 'geo' - geo coordinates regarding Earth overall
            -- 'pix' - coordinates in pixels regarding image
    '''

    # Earth radius
    R = 6373.0

    if tpe == 'geo':
        lat1 = radians(xy1[0])
        lon1 = radians(xy1[1])
        lat2 = radians(xy2[0])
        lon2 = radians(xy2[1])
    else:

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

# Custom SSIM metric in vector form
# Return scores
def ssim(x: torch.FloatTensor, y: torch.FloatTensor, coefs: dict) -> torch.FloatTensor:

    '''
    Vars:
        x - reference image
        y - matrix where each vector is flattened crop
    '''

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

# Simple RMSE metric in vector form
# Return torch.FloatTensor of scores
def rmse(x: torch.FloatTensor, y: torch.FloatTensor, coefs: dict) -> torch.FloatTensor:

    '''
    Vars:
        x - reference image
        y - matrix where each vector is flattened crop
    '''

    x = x.reshape(1, -1)
    score = torch.sqrt(torch.mean(torch.pow(x-y, 2), 1))
    return score

# Dev function for reference image preparation
# Return cropped image with window_size around point coordinate
def _prepare_ref_img(img: torch.FloatTensor, point_coor: Tuple[int],
                     window_size: Tuple[int]) -> torch.FloatTensor:

    '''
    Vars:
        img - image to be cropped
        point_coor - point coordinates (y, x)
        window_size - window size
    Exceptions:
        '0' - Out of bounds
    '''

    ref_window_lcx = point_coor[1]-window_size[1]//2
    ref_window_rcx = ref_window_lcx+window_size[1]
    ref_window_ucy = point_coor[0]-window_size[0]//2
    ref_window_dcy = ref_window_ucy+window_size[0]

    assert ref_window_lcx >= 0, '0'
    assert ref_window_rcx < img.shape[1], '0'
    assert ref_window_ucy >= 0, '0'
    assert ref_window_dcy < img.shape[0], '0'

    im = img[ref_window_ucy:ref_window_dcy, ref_window_lcx:ref_window_rcx]

    assert im[im<0].sum() == 0, '1' # Too noisy

    return im

def find_best_match(img1: torch.FloatTensor,
                    img2: torch.FloatTensor,
                    point_coor: Tuple[int],
                    window_size: Tuple[int],
                    vicinity_size: Tuple[int],
                    metric_fn: Callable[[torch.FloatTensor, torch.FloatTensor, dict], torch.FloatTensor],
                    device: str,
                    mode: str = 'max',
                    coefs: dict = None) -> Tuple:

    '''
    Vars:
        img1 - image where we pined point
        img2 - image where we want to find our point
        point_coor - point coordinates (y, x)
        window_size - window size
        vicinity_size - vicinity size
        metric_fn - metric function: metric_fn(crop1, crop2, coefs)
        device - device used
        mode - optimization mode
        coefs - parameters for metric function
    Exceptions:
        '0' - Out of bounds
        '1' - Too noisy
        'Dev exception' - Wrong functions usage
    '''

    assert mode in ['max', 'min'], 'Dev exception'

    assert point_coor[0] >= 0 and point_coor[0] < img2.shape[0], '0' # Out of bounds
    assert point_coor[1] >= 0 and point_coor[1] < img2.shape[1], '0'

    # Calculate reference image and vicinity coors
    ref_image = _prepare_ref_img(img1, point_coor, window_size)
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

    # Sample vicinity crops
    tmp1 = img1[vicinity_ucy:vicinity_dcy, vicinity_lcx:vicinity_rcx]
    tmp2 = img2[vicinity_ucy:vicinity_dcy, vicinity_lcx:vicinity_rcx]

    # Check if vicinity have enough of significant pixels
    assert tmp2[tmp2<0].sum()/(tmp2.shape[0]*tmp2.shape[1]) < .7, '1'
    assert tmp1[tmp1<0].sum()/(tmp1.shape[0]*tmp1.shape[1]) < .7, '1'

    # Prepare data
    idx = []
    yx = []
    imgs = torch.zeros((
        (vicinity_dcy-vicinity_ucy-window_size[0])*(vicinity_rcx-vicinity_lcx-window_size[1]),
        window_size[1]*window_size[0]
    )).to(device)

    # Collect moving windows crops
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
        return idx[l], scores[l].item()
    else:
        l = torch.argmin(scores).item()
        return idx[l], scores[l].item()

# Full inference function of getting point, vicinity and mask
# Return (y, x), velocity, mask or (y, x), velocity, mask
def inference(img1: torch.FloatTensor,
              img2: torch.FloatTensor,
              metadata: b0_proj_dt,
              dt: int,
              point_coor: Tuple[float],
              window_size: Tuple[int],
              vicinity_size: Tuple[int],
              metric_fn: Callable[[torch.FloatTensor, torch.FloatTensor, dict], torch.FloatTensor],
              device: str,
              mode: str = 'max',
              tpe: str = 'pix',
              coefs: dict = None,
              bef: float = None,
              sf: float = None) -> Tuple:

    '''
    Vars:
        img1 - image where we pined point
        img2 - image where we want to find our point
        metadata - metadata
        dt - time delta between images
        point_coor - point coordinates (y, x)
        window_size - window size
        vicinity_size - vicinity size
        metric_fn - metric function: metric_fn(crop1, crop2, coefs)
        device - device used
        mode - optimization mode
        tpe - coordinates type: 'geo' or 'pix'
        coefs - parameters for metric function
        bef - Backward Euclidean Filtering threshold or -1 if only loss needed
        sf - Score filtering threshold (recommend 0.5)
    Exceptions:
        '0' - Out of bounds
        '1' - Too noisy
        'Dev exception' - Wrong functions usage
    '''

    # If geo used then init ProjMapper as converter and convert coordinates
    if tpe == 'geo':
        converter = pm.ProjMapper(metadata['b0_proj_common']['projType']-1,
                               metadata['b0_proj_common']['lon'],
                               metadata['b0_proj_common']['lat'],
                               metadata['b0_proj_common']['lonSize'],
                               metadata['b0_proj_common']['latSize'],
                               metadata['b0_proj_common']['lonRes']/3600.0,
                               metadata['b0_proj_common']['latRes']/3600.0)

        point_coor = [converter.y(point_coor[0]), converter.x(point_coor[1])]


    # Calculate forward pass
    idx, score = find_best_match(img1, img2, point_coor, window_size,
                    vicinity_size, metric_fn,
                    device, mode, coefs)


    # If BEF is not None then calculate backward pass
    if not bef is None:
        idx_rev, score_rev = find_best_match(img2, img1, idx, window_size,
                        vicinity_size, metric_fn,
                        device, mode, coefs)

        loss = ((idx_rev[0]-point_coor[0])**2+(idx_rev[1]-point_coor[1])**2)**.5
        loss = loss/(vicinity_size[0]**2+vicinity_size[1]**2)**.5

    # Filtering
    mask = True
    if not sf is None:
        mask = score > sf
    if not bef is None:
        if bef > 0:
            mask = mask * (loss < bef)

    # Convert coordinates to geo back
    if tpe == 'geo':
        idx = [converter.lat(idx[0]), converter.lon(idx[1])]
        point_coor = [converter.lat(point_coor[0]), converter.lon(point_coor[1])]

    distance = calculate_distance(metadata, idx, point_coor, tpe=tpe)
    velocity = distance/dt


    if bef is None or bef > 0:
        return idx, velocity, mask
    elif bef == -1:
        return idx, velocity, loss, mask