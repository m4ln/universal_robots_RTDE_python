''' This file is for the configuration of the robot and the control loop.'''

# Define the robot's host IP and port
ROBOT_HOST = "169.254.91.163"
ROBOT_PORT = 30004

# small value for small deviation
EPSILON = 0.001

# enter the configuration of the tcp points you want to use
tcp_pos_config = [0,1]

# TCP positions (x,y,z,rx,ry,rz in base view) between which the robot moves
tcp_pos_0 = [-0.119, -0.528, 0.388, 0.03, -2.8, 1.5]
tcp_pos_1 = [-0.119, -0.528, 0.388, 0.13, -2.8, 1.5]

# daniel
tcp_pos_0 = [-0.12, -0.51, 0.21, 0, 3.11, 0.04]
tcp_pos_1 = [-0.12, -0.51, 0.21, 0.2, 3.11, 0.04]
tcp_pos_2 = [-0.12, -0.51, 0.21, 0, 3.11, 0.14]

# tcp_pos_0 = [-0.084, -0.252, 0.121, 2.249, 2.117, 0.131]
# tcp_pos_1 = tcp_pos_0.copy()
# tcp_pos_1[0] += EPSILON
# tcp_pos_2 = [-0.129, -0.303, 0.11, 2.24, 1.281, -0.095]
# tcp_pos_3 = [-0.13, -0.324, 0.451, 1.3, 1.233, -1.209]

# tcp_pos_0 = [0.245, -0.0973, 0.0959, 2.248, -2.189, 0.079]
# tcp_pos_1 = [0.245, -0.4043, 0.0959, 2.248, -2.189, 0.079]
# tcp_pos_2 = [0.081, -0.259, 0.1546, 1.265, -2.686, 0.008]
tcp_pos_3 = [0.154, -0.2, 0.273, 1.974, -3.886, -1.485]
tcp_pos_4 = [0.154, -0.2, 0.273, 1.974, -3.886, -1.49]
# tcp_pos_4 = [-0.033, -0.251, 0.273, 0.359, -4.698, 0.233]
tcp_pos_5 = [0.09643, -0.33, 0.532, 0.399, 2.318, -0.225]
tcp_pos_6 = [-0.120, -0.315, 0.287, 0.331, 2.355, -0.093]
tcp_pos_7 = [0.09643, -0.33, 0.532, 0.399, 2.32, -0.225]
tcp_pos_8 = [0.154, -0.2, 0.273, 1.98, -3.886, -1.485] # tcp5
tcp_pos_9 = [0.154, -0.2, 0.273, 1.974, -3.886, -1.49]#tcp4 [-0.61, -0.17, 0.97, 1.22, 1.14, 1.06]
tcp_pos_10 = [0.081, -0.259, 0.1546, 1.265, -2.69, 0.008] # tcp3 [-0.33, -0.42, 0.24, 0.04, 0.48, -0.36]
tcp_pos_11 = [0.245, -0.4043, 0.0959, 2.248, -2.19, 0.079] # tcp2 [-0.48, -0.16, 0.35, 0.3, 0.68, -0.68]

# tcp_pos_9 = tcp_pos_4 # tcp_pos_8
# tcp_pos_10 = tcp_pos_3 # tcp_pos_9
# tcp_pos_11 = tcp_pos_4 # tcp_pos_7

# enter the configuration of the tcp points you want to use
tcp_poses_sel = []
# make a list of the tcp points you want to use
for pos in tcp_pos_config:
    tcp_poses_sel.append(globals()["tcp_pos_%i" % pos])

tcp_poses_all = []
# make a dynaminc list of tcp positions
for i in range(12):
    tcp_poses_all.append(globals()["tcp_pos_%i" % i])

