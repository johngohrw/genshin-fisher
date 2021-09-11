import cv2
import pyautogui
import pygetwindow as gw
import numpy as np
import time
method = cv2.TM_CCOEFF_NORMED

# load template matching images
bite = cv2.imread('templates/gotabite3.png', cv2.IMREAD_UNCHANGED)

left1 = cv2.imread('templates/proper/left_1.png')
left2 = cv2.imread('templates/proper/left_2.png')
left3 = cv2.imread('templates/proper/left_3.png')
left4 = cv2.imread('templates/proper/left_4.png')
right1 = cv2.imread('templates/proper/right_1.png')
right2 = cv2.imread('templates/proper/right_2.png')
right3 = cv2.imread('templates/proper/right_3.png')
right4 = cv2.imread('templates/proper/right_4.png')
cursor1 = cv2.imread('templates/proper/cursor_1.png')
cursor2 = cv2.imread('templates/proper/cursor_2.png')
cursor3 = cv2.imread('templates/proper/cursor_3.png')
cursor4 = cv2.imread('templates/proper/cursor_4.png')

left_templates = [left1, left2, left3, left4]
right_templates = [right1, right2, right3, right4]
cursor_templates = [cursor1, cursor2, cursor3, cursor4]

bite_rows,bite_cols = bite.shape[:2]
# leftbound_rows,leftbound_cols = leftbound.shape[:2]
# rightbound_rows,rightbound_cols = rightbound.shape[:2]
# cursor_rows,cursor_cols = cursor.shape[:2]

# template matching threshold
threshold = 0.8
bite_threshold = 0.9
cache_delay_threshold = 4
bite_cache_delay_threshold = 75

l_x_cache = None;
l_x_cache_delay = 0;
c_x_cache = None;
c_x_cache_delay = 0;
r_x_cache = None;
r_x_cache_delay = 0;
b_cache_delay = 0;

while True:
    genshinWindow = gw.getWindowsWithTitle("Genshin Impact")[0]
    # detecting genshin window
    if (genshinWindow and genshinWindow.top > -100 and genshinWindow.left > -100):
        # genshin window is active
        w, h, x, y =  genshinWindow.width, genshinWindow.height, genshinWindow.left, genshinWindow.top
        # print(x, y, w, h)

        # get screengrab of genshin window region with 
        # window title bar cropped, assuming titlebar is 24px in height.
        # only grabs the top half & middle of the window to reduce processing
        genshinTopRegion = pyautogui.screenshot(region=(x + (w//2) - 250, y + 120, 500, 130))
        genshinTopRegion = cv2.cvtColor(np.array(genshinTopRegion), cv2.COLOR_RGB2BGR)

        # auto clicking upon bite
        b_cache_delay += 1
        b_val = 0
        if (b_cache_delay > bite_cache_delay_threshold):
            bite_result = cv2.matchTemplate(genshinTopRegion, bite[..., :3], method, mask=bite[..., 3])
            _, b_val, _, b_x = cv2.minMaxLoc(bite_result)
        b_cache_delay += 1
        if (b_val >= bite_threshold and b_val <= 1 and b_cache_delay > bite_cache_delay_threshold):
            print("bite detected, clicking for 0.5 sec")
            cv2.rectangle(genshinTopRegion, b_x,(b_x[0]+bite_cols,b_x[1]+bite_rows),(0,255,0),1)
            pyautogui.mouseDown()
            time.sleep(0.5)
            pyautogui.mouseUp()
            b_cache_delay = 0
            
        # # match template with whatever's on screen
        leftmax = 0
        for image in left_templates:
            left_result = cv2.matchTemplate(genshinTopRegion, image, method)
            _, l_val, _, l_x = cv2.minMaxLoc(left_result)
            if l_val > leftmax:
                leftmax = l_val
                left_rows,left_cols = image.shape[:2]
        l_val = leftmax
        if (l_val >= threshold):
            cv2.rectangle(genshinTopRegion, l_x,(l_x[0]+left_cols,l_x[1]+left_rows),(0,0,255),1)
            l_x_cache = l_x
            
        rightmax = 0
        for image in right_templates:
            right_result = cv2.matchTemplate(genshinTopRegion, image, method)
            _, r_val, _, r_x = cv2.minMaxLoc(right_result)
            if r_val > rightmax:
                rightmax = r_val
                right_rows,right_cols = image.shape[:2]
        r_val = rightmax
        if (r_val >= threshold):
            cv2.rectangle(genshinTopRegion, r_x,(r_x[0]+right_cols,r_x[1]+right_rows),(0,0,255),1)
            r_x_cache = r_x
        
        cursormax = 0
        for image in cursor_templates:
            cursor_result = cv2.matchTemplate(genshinTopRegion, image, method)
            _, c_val, _, c_x = cv2.minMaxLoc(cursor_result)
            if c_val > cursormax:
                cursormax = c_val
                cursor_rows,cursor_cols = image.shape[:2]
        c_val = cursormax
        if (c_val >= threshold):
            cv2.rectangle(genshinTopRegion, c_x,(c_x[0]+cursor_cols,c_x[1]+cursor_rows),(0,0,255),1)
            c_x_cache = c_x
        
        # process caches if its not found
        if (l_val < threshold):
            # if still within grace period
            if (l_x_cache_delay < cache_delay_threshold):
                l_x = l_x_cache  # reuse cached x
                l_x_cache_delay += 1
            # not in grace period
            else:
                l_x_cache_delay = 0
                l_x = None
                l_x_cache = None
        if (c_val < threshold):
            if (c_x_cache_delay < cache_delay_threshold):
                c_x = c_x_cache
                c_x_cache_delay += 1
            else:
                c_x_cache_delay = 0
                c_x = None
                c_x_cache = None
        if (r_val < threshold):
            if (r_x_cache_delay < cache_delay_threshold):
                r_x = r_x_cache
                r_x_cache_delay += 1
            else:
                r_x_cache_delay = 0
                r_x = None
                r_x_cache = None

        print(l_x, " - ", c_x," - ", r_x)
        
        if (r_x and c_x):
            rx = r_x[0]
            cx = c_x[0]
            if (cx + 100 < rx):
                print("    <  I------->")
                pyautogui.mouseDown()
                time.sleep(0.2)
                pyautogui.mouseUp()
            elif (cx + 40 < rx):
                print("    <     I---->")
                pyautogui.mouseDown()
                time.sleep(0.02)
                pyautogui.mouseUp()
            
        if (l_x and c_x):
            lx = l_x[0]
            cx = c_x[0]
            if (cx < lx):
                print("I---<          >")
                pyautogui.mouseDown()
                time.sleep(0.2)
                pyautogui.mouseUp()

        cv2.imshow('output', genshinTopRegion)
        key = cv2.waitKey(1)
        if key == 27:
            cv2.destroyAllWindows()
