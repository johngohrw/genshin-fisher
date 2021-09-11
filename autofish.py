import cv2
import pyautogui
import pygetwindow as gw
import numpy as np
import time
method = cv2.TM_CCOEFF_NORMED

# template matching images
bite = cv2.imread('gotabite3.png', cv2.IMREAD_UNCHANGED)
bite_rows,bite_cols = bite.shape[:2]
leftbound = cv2.imread('left4.png')
leftbound_rows,leftbound_cols = leftbound.shape[:2]
rightbound = cv2.imread('right4.png')
rightbound_rows,rightbound_cols = rightbound.shape[:2]
cursor = cv2.imread('cursor3.png')
cursor_rows,cursor_cols = cursor.shape[:2]

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
        left_result =  cv2.matchTemplate(genshinTopRegion, leftbound, method)
        right_result =  cv2.matchTemplate(genshinTopRegion, rightbound, method)
        cursor_result =  cv2.matchTemplate(genshinTopRegion, cursor, method)

        # get minmax and accuracy value
        _, l_val, _, l_x = cv2.minMaxLoc(left_result)
        _, r_val, _, r_x = cv2.minMaxLoc(right_result)
        _, c_val, _, c_x = cv2.minMaxLoc(cursor_result)
        
        # print(l_val, r_val, c_val)

        if (l_val >= threshold):
            cv2.rectangle(genshinTopRegion, l_x,(l_x[0]+leftbound_cols,l_x[1]+leftbound_rows),(0,0,255),1)
            l_x_cache = l_x
        if (r_val >= threshold):
            cv2.rectangle(genshinTopRegion, r_x,(r_x[0]+leftbound_cols,r_x[1]+leftbound_rows),(255,0,0),1)
            r_x_cache = r_x
        if (c_val >= threshold):
            cv2.rectangle(genshinTopRegion, c_x,(c_x[0]+cursor_cols,c_x[1]+cursor_rows),(0,255,0),1)
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

        # print(l_x, " - ", c_x," - ", r_x)
            
        
        if (l_x is not None and c_x is not None):
            # I  <  >
            if (c_x[0] < l_x[0]):
                pyautogui.mouseDown()
                time.sleep(0.16)
                pyautogui.mouseUp()

                print("click", "I  <      >")

        if (r_x is not None and c_x is not None):
            # I--100-<--->
            if (c_x[0] + 80 < r_x[0] ):
                pyautogui.mouseDown()
                time.sleep(0.12)
                pyautogui.mouseUp()
                print("click", "<I         >")
             # <  I--20-->
            elif (c_x[0] + 40 < r_x[0]):
                pyautogui.mouseDown()
                time.sleep(0.05)
                pyautogui.mouseUp()
                print("click", "<         I >")

        # if (l_x is not None and c_x is not None):
        #     if (l_x[0] > c_x[0]):
        #         clicktime = 0.0005 * (l_x[0] - c_x[0]) + 0.1
        #         pyautogui.mouseDown()
        #         time.sleep(clicktime)
        #         pyautogui.mouseUp()
        #         print("click", "I  <      >", c_x[0], l_x[0], clicktime, "s")

        # if (r_x is not None and c_x is not None):
        #     # I--70-<--->
        #     if (c_x[0] + 70 < r_x[0] ):
        #         pyautogui.mouseDown()
        #         time.sleep(0.12)
        #         pyautogui.mouseUp()
        #         print("click", "<I         >", c_x[0] + 70, r_x[0])
        #      # <  I--20-->
        #     elif (c_x[0] + 10 < r_x[0]):
        #         pyautogui.mouseDown()
        #         time.sleep(0.05)
        #         pyautogui.mouseUp()
        #         print("click", "<         I >", c_x[0] + 30, r_x[0])
                
    
        cv2.imshow('output', genshinTopRegion)
        key = cv2.waitKey(1)
        if key == 27:
            cv2.destroyAllWindows()

    time.sleep(0.001)