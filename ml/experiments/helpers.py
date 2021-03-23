import numpy as np

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

def luminace(x, y, k1=0.01, L=(2**16 - 1)):
    x = x.reshape(-1)
    y = y.reshape(-1)
    x = x[~np.isnan(x)]
    y = y[~np.isnan(y)]
    nu_x = x.mean()
    nu_y = y.mean()
    l = (2*nu_x*nu_y + (k1*L)**2)/(nu_x**2 + nu_y**2 + (k1*L)**2)
    
    return l

def normalize(data):
    data = data/data.max()
    data[data < 0] = np.nan
    return data


def rmse(data1, data2, coefs):
    data1 = data1[~np.isnan(data1)].reshape(-1)
    data2 = data2[~np.isnan(data2)].reshape(-1)
    return np.sqrt(((data1-data2)**2).sum()/data1.shape[0])

def ssim(data1, data2, coefs):
    x = data1[~np.isnan(data1)].reshape(-1)
    y = data2[~np.isnan(data2)].reshape(-1)
    
    nu_x = x.mean()
    nu_y = y.mean()
    var_x = np.var(x)
    var_y = np.var(y)
    covar = ((x-nu_x)*(y-nu_y)).mean()
    c1 = (coefs['k1']*coefs['L'])**2
    c2 = (coefs['k2']*coefs['L'])**2
    c3 = c2/2
    
    l = (2*nu_x*nu_y+c1)/(nu_x**2 + nu_y**2 + c1)
    c = (2*var_x*var_y + c2)/(var_x**2 + var_y**2 + c1)
    s = (covar + c3)/(var_x*var_y + c3)
    
    return l*c*s
    

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
    
    halfv0 = vicinity_size[0]//2 if vicinity_size[0]%2 == 0 else (vicinity_size[0]+1)//2
    halfv1 = vicinity_size[1]//2 if vicinity_size[1]%2 == 0 else (vicinity_size[1]+1)//2
    
    halfw0 = window_size[0]//2 if window_size[0]%2 == 0 else (window_size[0]+1)//2
    halfw1 = window_size[1]//2 if window_size[1]%2 == 0 else (window_size[1]+1)//2
    
    ref_image = img1[point_coor[0]-halfw0:point_coor[0]+halfw0, point_coor[1]-halfw1:point_coor[1]+halfw1]
    best_score = -float('infinity') if mode == 'max' else float('infinity')
    best_idx = [None, None]
    
    for i in range(point_coor[0]-halfv0, point_coor[0]+halfv0-halfw0*2):
        for j in range(point_coor[1]-halfv1, point_coor[1]+halfv1-halfw1*2):
            score = metric_fn(ref_image, img2[i:i+halfw0*2, j:j+halfw1*2], coefs)
            tmp = mode_comp(score, best_score, mode)
            if tmp == score:
                best_score = tmp
                best_idx[0] = i
                best_idx[1] = j
    return best_idx, best_score
            
            
            
            
            
    
    
    
    
    
    
    
    
    
    
    
    