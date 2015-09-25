import math
# set max

def transition(value, max, start, end):
    '''Calculate the transition value of a given value'''
    return start + (end - start) * value / max

def transition_r(value, max, start, end):
    '''Calculate the transition value of triplets of RGB and HSV'''
    r1 = transition(value, max, start[0], end[0])
    r2 = transition(value, max, start[1], end[1])
    r3 = transition(value, max, start[2], end[2])
    return (r1, r2, r3)

def rgb_to_hsv(r, g, b):
    '''Convert RGB triplets to HSV'''
    max_r = max(r, g, b)
    min_r = min(r, g, b)
    v = max_r
    if min_r == max_r:
        return (0, 0, v)
    diff = max_r - min_r
    s = diff / max_r
    rr = (max_r - r)/ diff
    gr = (max_r - g)/ diff
    br = (max_r - b)/ diff
    
    if r == max_r:
        h = br - gr
    elif g == max_r:
        h = 2.0 + rr - br
    else: 
        h = 4.0 + gr - rr
    h = (h / 6.0) % 1.0
    return (h , s, v)   
    
def hsv_to_rgb(h, s, v):
    '''Convert HSV triplets to RGB'''
    if s == 0.0:
        return (v, v, v)
    i = int(math.floor(h * 6.0))
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    if i % 6 == 0:
        return (round(v), round(t), round(p))
    if i == 1:
        return (round(q), round(v), round(p))
    if i == 2:
        return (round(p), round(v), round(t))
    if i == 3:
        return (round(p), round(q), round(v))
    if i == 4:
        return (round(t), round(p), round(v))
    if i == 5:
        return (round(v), round(p), round(q))
    


    
def color_scale(max, value):
    '''Return RGB triplet between yellow(high) to blue(low)'''
    
    # The higher the expression level, more "yellow" will appear
    if value >= 0:
        #set start to red 
        start = rgb_to_hsv(255, 0, 0)
        #set end to yellow
        end = rgb_to_hsv(255, 255, 0)
        
    # The lower the expression level, more "blue" will appear
    # Return RGB triplet between red to blue
    else:
        #set start to red 
        start = rgb_to_hsv(255, 0, 0)
        #set end to blue
        end = rgb_to_hsv(0, 0, 255) 
    
    
    hsv_triplet = transition_r(value, max, start, end)
    rgb_triplet = hsv_to_rgb(abs(hsv_triplet[0]), abs(hsv_triplet[1]), abs(hsv_triplet[2]))
    return rgb_triplet

if __name__ == "__main__":
	print color_scale(100, 100)

