import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time

# --- Configuration ---
SCREEN_W, SCREEN_H = pyautogui.size()
CAM_W, CAM_H = 1280, 720
FRAME_REDUCTION = 150 
SMOOTHING = 5

PINCH_DIST_THRESHOLD = 30
CLICK_DIST_THRESHOLD = 35
SWIPE_DIST_THRESHOLD = 200
SWIPE_COOLDOWN = 0.8

# --- Initialization ---
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.75,
    min_tracking_confidence=0.75
)
mp_draw = mp.solutions.drawing_utils

def count_fingers(lm_list):
    fingers = []
    # Thumb (based on x-coordinate relative to MCP joint for right hand)
    # We use a more robust check for thumb
    if lm_list[4][1] > lm_list[3][1]:
        fingers.append(1)
    else:
        fingers.append(0)
    
    # 4 Fingers (based on y-coordinate relative to PIP joint)
    tips = [8, 12, 16, 20]
    pips = [6, 10, 14, 18]
    for i in range(4):
        if lm_list[tips[i]][2] < lm_list[pips[i]][2]:
            fingers.append(1)
        else:
            fingers.append(0)
    return fingers # [thumb, index, middle, ring, pinky]

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    cap.set(3, CAM_W)
    cap.set(4, CAM_H)

    p_loc_x, p_loc_y = 0, 0
    swipe_x_start = 0
    is_swiping = False
    last_swipe_time = 0
    last_action_time = 0

    print("=== AI Vision PC Automation ===")
    print("🚀 CONTROLS:")
    print("- One Finger (Index): Move Cursor")
    print("- Pinch Index + Middle: Left Click")
    print("- Pinch Middle + Ring: Right Click")
    print("- Pinch Index + Thumb: Take Screenshot")
    print("- Two Fingers Up (Index + Middle): Scroll Mode")
    print("- Rapid Side Swipe: Switch Tabs")
    print("- Full Fist: Show/Hide Desktop (Win+D)")
    print("Press 'q' in the window to EXIT.")

    while True:
        success, img = cap.read()
        if not success:
            break

        img = cv2.flip(img, 1)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)

        # Draw Control Region
        cv2.rectangle(img, (FRAME_REDUCTION, FRAME_REDUCTION), 
                     (CAM_W - FRAME_REDUCTION, CAM_H - FRAME_REDUCTION), 
                     (0, 255, 255), 2)

        if results.multi_hand_landmarks:
            for hand_lms in results.multi_hand_landmarks:
                lm_list = []
                for id, lm in enumerate(hand_lms.landmark):
                    cx, cy = int(lm.x * CAM_W), int(lm.y * CAM_H)
                    lm_list.append([id, cx, cy])

                if lm_list:
                    fingers = count_fingers(lm_list)
                    
                    # Landmarks: Thumb(4), Index(8), Middle(12), Ring(16), Pinky(20)
                    idx_x, idx_y = lm_list[8][1:]
                    mid_x, mid_y = lm_list[12][1:]
                    rng_x, rng_y = lm_list[16][1:]
                    thm_x, thm_y = lm_list[4][1:]
                    x_wrist = lm_list[0][1]

                    # --- 1. MOUSE MOVEMENT (Only Index up) ---
                    if fingers[1] == 1 and fingers[2] == 0:
                        x3 = np.interp(idx_x, (FRAME_REDUCTION, CAM_W - FRAME_REDUCTION), (0, SCREEN_W))
                        y3 = np.interp(idx_y, (FRAME_REDUCTION, CAM_W - FRAME_REDUCTION), (0, SCREEN_H))
                        c_loc_x = p_loc_x + (x3 - p_loc_x) / SMOOTHING
                        c_loc_y = p_loc_y + (y3 - p_loc_y) / SMOOTHING
                        pyautogui.moveTo(c_loc_x, c_loc_y)
                        p_loc_x, p_loc_y = c_loc_x, c_loc_y
                        cv2.circle(img, (idx_x, idx_y), 10, (255, 0, 0), cv2.FILLED)

                    # --- 2. LEFT CLICK (Pinch Index & Middle) ---
                    dist_l = np.hypot(idx_x - mid_x, idx_y - mid_y)
                    if dist_l < CLICK_DIST_THRESHOLD:
                         if time.time() - last_action_time > 0.3:
                            cv2.circle(img, (idx_x, idx_y), 15, (0, 255, 0), cv2.FILLED)
                            pyautogui.click()
                            print("Left Click")
                            last_action_time = time.time()

                    # --- 3. RIGHT CLICK (Pinch Middle & Ring) ---
                    dist_r = np.hypot(mid_x - rng_x, mid_y - rng_y)
                    if dist_r < CLICK_DIST_THRESHOLD:
                        if time.time() - last_action_time > 0.3:
                            cv2.circle(img, (mid_x, mid_y), 15, (0, 0, 255), cv2.FILLED)
                            pyautogui.rightClick()
                            print("Right Click")
                            last_action_time = time.time()

                    # --- 4. SCROLLING (Index + Middle up but NOT pinching) ---
                    elif fingers[1] == 1 and fingers[2] == 1 and dist_l > CLICK_DIST_THRESHOLD:
                        scroll_amount = (idx_y - p_loc_y) * 2
                        pyautogui.scroll(-int(scroll_amount))
                        p_loc_y = idx_y # Update p_loc_y specifically for relative scrolling
                        cv2.putText(img, "SCROLLING", (idx_x, idx_y-20), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)

                    # --- 5. SCREENSHOT (Pinch Thumb & Index) ---
                    dist_s = np.hypot(idx_x - thm_x, idx_y - thm_y)
                    if dist_s < PINCH_DIST_THRESHOLD:
                        if time.time() - last_action_time > 2.0:
                            print("📸 Screenshot taken!")
                            pyautogui.screenshot(f"screenshot_{int(time.time())}.png")
                            last_action_time = time.time()
                            cv2.putText(img, "SCREENSHOT!", (500, 350), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)

                    # --- 6. SWIPE (TAB SWITCHING) ---
                    if not is_swiping:
                        swipe_x_start = x_wrist
                        is_swiping = True
                        last_swipe_time = time.time()
                    else:
                        if time.time() - last_swipe_time < 0.4:
                            diff = x_wrist - swipe_x_start
                            if abs(diff) > SWIPE_DIST_THRESHOLD:
                                if diff > 0:
                                    pyautogui.hotkey('ctrl', 'tab')
                                else:
                                    pyautogui.hotkey('ctrl', 'shift', 'tab')
                                is_swiping = False
                                time.sleep(0.5)
                        else:
                            is_swiping = False

                    # --- 7. SHOW DESKTOP (FIST) ---
                    if sum(fingers) == 0:
                        if time.time() - last_action_time > 1.5:
                            print("👊 Fist: Win+D")
                            pyautogui.hotkey('win', 'd')
                            last_action_time = time.time()

                mp_draw.draw_landmarks(img, hand_lms, mp_hands.HAND_CONNECTIONS)

        cv2.imshow("Vision Control", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
