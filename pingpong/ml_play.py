"""
The template of the script for the machine learning process in game pingpong
"""

# Import the necessary modules and classes
from mlgame.communication import ml as comm
import os.path as path
import pickle
import numpy as np

def ml_loop(side: str):
    """
    The main loop for the machine learning process

    The `side` parameter can be used for switch the code for either of both sides,
    so you can write the code for both sides in the same script. Such as:
    ```python
    if side == "1P":
        ml_loop_for_1P()
    else:
        ml_loop_for_2P()
    ```

    @param side The side which this script is executed for. Either "1P" or "2P".
    """

    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here
    ball_served = False
    filename = path.join(path.dirname(__file__),"D:\\NCKU\\2\\2-2\ML\\MLGame-master\\games\\pingpong\\ml\\save\\SVMRegression_Ball_x_4.0_0.1.pickle")
    with open(filename, 'rb') as file:
        svr_ball_x = pickle.load(file)
    """
    filename = path.join(path.dirname(__file__),"save\SVMRegression_Ball_y.pickle")
    with open(filename, 'rb') as file:
        svr_ball_y = pickle.load(file)"""
    
    PlatformPos2_pre = [80, 50]
    Blocker_pre = [0, 240]

    # 2. Inform the game process that ml process is ready
    comm.ml_ready()

    s = [93,93]
    def get_direction(ball_x,ball_y,ball_pre_x,ball_pre_y):
        VectorX = ball_x - ball_pre_x
        VectorY = ball_y - ball_pre_y
        if(VectorX>=0 and VectorY>=0):
            return 0
        elif(VectorX>0 and VectorY<0):
            return 1
        elif(VectorX<0 and VectorY>0):
            return 2
        elif(VectorX<0 and VectorY<0):
            return 3

    # 3. Start an endless loop
    while True:
        # 3.1. Receive the scene information sent from the game process
        scene_info = comm.recv_from_game()
        feature = []
        #feature.append(scene_info['frame'])
        feature.append(scene_info['ball'][0])
        feature.append(scene_info['ball'][1])
        feature.append(scene_info['ball_speed'][0])
        feature.append(scene_info['ball_speed'][1])
        #feature.append(scene_info['platform_2P'][0])
        #feature.append(scene_info['platform_2P'][1])
        feature.append(scene_info['blocker'][0])
        #feature.append(scene_info['blocker'][1])

        #PlatformPos2 = feature[:, 5:7]
        #PlatformPos2_pre = np.array(PlatformPos2[1:])
        #vectors_2P = PlatformPos2_pre - scene_info['platform_2P']#用連續兩個frame的x,y相減得到2P的移動向量    
        #data = np.hstack((data[1:, :], vectors_2P))#9 10
        
        #feature.append(PlatformPos2_pre[0] - scene_info['platform_2P'][0])
        #feature.append(PlatformPos2_pre[1] - scene_info['platform_2P'][1])
        #PlatformPos2_pre = scene_info['platform_2P']

        #Blocker = data[:, 7:9]
        #Blocker_next = np.array(Blocker[1:])
        #vectors_Blocker = Blocker_pre - scene_info['blocker']#用連續兩個frame的x,y相減得到Blocker的移動向量    
        #data = np.hstack((data[1:, :], vectors_Blocker))#11 12
        feature.append(Blocker_pre[0] - scene_info['blocker'][0])
        #feature.append(Blocker_pre[1] - scene_info['blocker'][1])
        Blocker_pre = scene_info['blocker']
        
        feature.append(get_direction(feature[0],feature[1],s[0],s[1]))
        s = [feature[0], feature[1]]
        feature = np.array(feature)
        feature = feature.reshape((-1,7))
        print(feature.shape)
        # 3.2. If either of two sides wins the game, do the updating or
        #      resetting stuff and inform the game process when the ml process
        #      is ready.
        if scene_info["status"] != "GAME_ALIVE":
            # Do some updating or resetting stuff
            ball_served = False

            # 3.2.1 Inform the game process that
            #       the ml process is ready for the next round
            comm.ml_ready()
            continue

        # 3.3 Put the code here to handle the scene information

        # 3.4 Send the instruction for this frame to the game process
        if not ball_served:
            comm.send_to_game({"frame": scene_info["frame"], "command": "SERVE_TO_LEFT"})
            ball_served = True
        else:

            plat_x, plat_y = scene_info['platform_1P']
            #m = scene_info['ball_speed'][1]/scene_info['ball_speed'][0]
            #feature = feature[:,:]
            
            #ball_y = svr_ball_y.predict(feature)

            if scene_info['ball'][1] > 240 or scene_info['ball_speed'][1] > 0: # 球往下

                ball_x = svr_ball_x.predict(feature)
                print(ball_x)
                if plat_x + 20 - ball_x > 3:
                    comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_LEFT"})
                elif plat_x + 20 - ball_x < -3:
                    comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_RIGHT"})
                else:
                    comm.send_to_game({"frame": scene_info["frame"], "command": "NONE"})
            """
            if scene_info['ball_speed'][1] > 0: # 球往下
                plat_x_next = ball_x - (ball_y - 420)/m
                if plat_x + 20 - plat_x_next > 0:
                    comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_LEFT"})
                elif plat_x + 20 - plat_x_next < 0:
                    comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_RIGHT"})
                else:
                    comm.send_to_game({"frame": scene_info["frame"], "command": "NONE"})
            """
            """
            if scene_info['ball_speed'][1] > 0: # 球往下
                if scene_info['ball_speed'][0] > 0: # 球往右

                    if ball_x - (ball_y - 420)/m > 200: # 會碰到右邊
                        boundR = ball_y - m*(ball_x - 200)
                        m2 = -m
                        plat_x_next = 200 - (boundR - 420)/m2
                        if plat_x + 20 - plat_x_next > 0:
                            comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_LEFT"})
                        elif plat_x + 20 - plat_x_next < 0:
                            comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_RIGHT"})
                        else:
                            comm.send_to_game({"frame": scene_info["frame"], "command": "NONE"})

                    else: #不會碰到右邊
                        plat_x_next = ball_x - (ball_y - 420)/m
                        if plat_x + 20 - plat_x_next > 0:
                            comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_LEFT"})
                        elif plat_x + 20 - plat_x_next < 0:
                            comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_RIGHT"})
                        else:
                            comm.send_to_game({"frame": scene_info["frame"], "command": "NONE"})
                elif scene_info['ball_speed'][0] < 0: # 球往左

                    if ball_x - (ball_y - 420)/m < 0: # 會碰到左邊
                        boundL = ball_y - m*(ball_x)
                        m2 = -m
                        plat_x_next =  - (boundL - 420)/m2
                        if plat_x + 20 - plat_x_next > 0:
                            comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_LEFT"})
                        elif plat_x + 20 - plat_x_next < 0:
                            comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_RIGHT"})
                        else:
                            comm.send_to_game({"frame": scene_info["frame"], "command": "NONE"})

                    else: #不會碰到左邊
                        plat_x_next =  ball_x - (ball_y - 420)/m
                        if plat_x + 20 - plat_x_next > 0:
                            comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_LEFT"})
                        elif plat_x + 20 - plat_x_next < 0:
                            comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_RIGHT"})
                        else:
                            comm.send_to_game({"frame": scene_info["frame"], "command": "NONE"})
                else: # 垂直往下
                    if plat_x + 20 - plat_x_next > 0:
                            comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_LEFT"})
                    elif plat_x + 20 - plat_x_next < 0:
                        comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_RIGHT"})
                    else:
                        comm.send_to_game({"frame": scene_info["frame"], "command": "NONE"})"""
                        
            
