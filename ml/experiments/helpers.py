import numpy as np
import torch
import matplotlib as mpl
from math import sin, cos, sqrt, atan2, radians
from typing import List, Tuple, Callable

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

# Points generator
# Return list of points (y, x)
def generate_points(img, x0: int, y0: int, 
                    dx: int, dy: int, step: int, 
                    window_size: Tuple[int], nan_val: float = -100) -> Tuple[int]:
    
    '''
    Vars:
        img - numpy matrix
        x0 - initial x
        y0 - intitial y
        dx - window width
        dy - window height
        step - points frequency
        window_size - window size
        nan_val - NaN value to be replaced on
    '''
    
    points = []
    for x in range(x0+window_size[1]//2, x0+dx-window_size[1]//2, step):
        for y in range(y0+window_size[0]//2, y0+dy-window_size[0]//2, step):
            if img[y, x] != nan_val:
                points.append([y, x])
    return points

# Get color in certain color range
# Return color hex
def colorFader(c1: str, c2: str, mix: float = 0) -> str:
    
    '''
    Vars:
        c1 - initial color
        c2 - final color
        mix - [0, 1]
    Exceptions:
        'Dev exception' - Wrong functions usage
    '''
    
    assert mix >= 0 and mix <= 1, 'Dev exception'
    c1 = np.array(mpl.colors.to_rgb(c1))
    c2 = np.array(mpl.colors.to_rgb(c2))
    return mpl.colors.to_hex((1-mix)*c1 + mix*c2)

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
    
    ref_window_lcx = point_coor[1]-window_size[1]
    ref_window_rcx = point_coor[1]+window_size[1]
    ref_window_ucy = point_coor[0]-window_size[0]
    ref_window_dcy = point_coor[0]+window_size[0]
    
    assert ref_window_lcx >= 0, '0'
    assert ref_window_rcx-1 < img.shape[1], '0'
    assert ref_window_ucy >= 0, '0'
    assert ref_window_dcy-1 < img.shape[0], '0'
    
    im = img[ref_window_ucy:ref_window_dcy+1, ref_window_lcx:ref_window_rcx+1]
    assert (im<0).sum() == 0, '1' # Too noisy
    
    return im

def backforward_find(img1: torch.FloatTensor, 
                    img2: torch.FloatTensor, 
                    point_coor: Tuple[int], 
                    window_size: Tuple[int], 
                    vicinity_size: Tuple[int], 
                    metric_fn: Callable[[torch.FloatTensor, torch.FloatTensor, dict], torch.FloatTensor],
                    device: str = 'cpu') -> Tuple:
    
    '''
    Vars:
        img1 - image where we pined point
        img2 - image where we want to find our point
        point_coor - point coordinates (y, x)
        window_size - window size
        vicinity_size - vicinity size
        metric_fn - metric function: metric_fn(crop1, crop2, coefs)
        device - device used
    Exceptions:
        '0' - Out of bounds
        '1' - Too noisy
        'Dev exception' - Wrong functions usage
    '''
        
    assert point_coor[0] >= 0 and point_coor[0] < img2.shape[0], '0' # Out of bounds
    assert point_coor[1] >= 0 and point_coor[1] < img2.shape[1], '0'
    
    # Calculate reference image and vicinity coors
    ref_image = _prepare_ref_img(img1, point_coor, window_size)
    vicinity_lcx = point_coor[1]-vicinity_size[1]
    vicinity_rcx = point_coor[1]+vicinity_size[1]
    
    # BADTRIP HANDLER 1
    if vicinity_lcx < 0:
        vicinity_lcx = 0
        vicinity_rcx = vicinity_size[1]*2+1
        print('badtrip handler 1')
    # BADTRIP HANDLER 2
    if vicinity_rcx >= img2.shape[1]:
        vicinity_rcx = img2.shape[1]-1
        vicinity_lcx = vicinity_rcx - 2*vicinity_size[1]
        if vicinity_lcx < 0:
            vicinity_lcx = 0
        print('badtrip handler 2')
    
    vicinity_ucy = point_coor[0]-vicinity_size[0]
    vicinity_dcy = point_coor[0]+vicinity_size[0]
    
    # BADTRIP HANDLER 3
    if vicinity_ucy < 0:
        vicinity_ucy = 0
        vicinity_dcy = vicinity_size[0]*2+1
        print('badtrip handler 3')
    # BADTRIP HANDLER 4
    if vicinity_dcy >= img2.shape[0]:
        vicinity_dcy = img2.shape[0]-1
        vicinity_ucy = vicinity_dcy - 2*vicinity_size[0]
        if vicinity_ucy < 0:
            vicinity_ucy = 0
        print('badtrip handler 4')
    
    
    # Sample vicinity crops
    tmp1 = img1[vicinity_ucy:vicinity_dcy+1, vicinity_lcx:vicinity_rcx+1]
    tmp2 = img2[vicinity_ucy:vicinity_dcy+1, vicinity_lcx:vicinity_rcx+1]
    
    # Check if vicinity have enough of significant pixels
    assert (tmp2<0).sum()/(tmp2.shape[0]*tmp2.shape[1]) < .7, '1'
    assert (tmp1<0).sum()/(tmp1.shape[0]*tmp1.shape[1]) < .7, '1'
    
    # Prepare data
    h = vicinity_dcy-vicinity_ucy-window_size[0]*2+1
    w = vicinity_rcx-vicinity_lcx-window_size[1]*2+1
    idx = []
    imgs = torch.zeros((
        w*h,
        (window_size[1]*2+1)*(window_size[0]*2+1)
    )).to(device)
    
    # Collect moving windows crops
    c = 0
    for y in range(vicinity_ucy, vicinity_dcy-window_size[0]*2+1):
        for x in range(vicinity_lcx, vicinity_rcx-window_size[1]*2+1):
            
            idx.append([y+window_size[0], x+window_size[1]])
            img2_crop = img2[y:y+window_size[0]*2+1, x:x+window_size[1]*2+1]
            imgs[c] = img2_crop.reshape(-1)
            c += 1
    
    scores = metric_fn(ref_image, imgs)
    return idx, scores