from datetime import datetime
from time import monotonic

from src.backend.error.standby_transition import StandbyTransition
from src.backend.external_management.connections import Ext
from src.backend.sensor_fusion.tracking import (
    find_in_image, create_ray, locate_object, store_location, get_location_history, clear_location_history
)
from src.backend.state_management.error_checker import verify_track
from src.backend.state_management.state_manager import Manager, State
from src.backend.arm_control.trajectory import simple_trajectory
from src.backend.arm_control.kinematics import pos_to_arm_angles, R_TO_D
from src.frontend.gui import Gui
from src.frontend.visualisation import Graph


def post_msg(msg: str, gui: Gui, is_error):
    """Formats and prints message to GUI and console.
    """
    log = format_log(msg, is_error)
    print(log)
    gui.add_log(log)


def format_log(msg: str, is_error: bool = False) -> str:
    """Adds timestamp to log message.
    :return: Log with time prepended
    """
    return f'{datetime.now().time()} {"!!" if is_error else "--"} {msg}'


def limit_joint_to_range(value: int, lower: int, upper: int, joint: str = 'joint', verbose: bool = False) -> int:
    """Limits a command for a given joint to a specified range.
    :return: The original value if it is within the range, otherwise the closest limit value
    """
    if value < lower:
        if verbose:
            print(f'{joint} increased from {value} to {lower}')
        return lower
    elif value > upper:
        if verbose:
            print(f'{joint} decreased from {value} to {upper}')
        return upper
    return value


def operation_loop(state_manager: Manager, connection_manager: Ext, gui: Gui, vis: Graph):
    # setup instances
    print('Preparing managers...')
    last_state = None
    log_file = open('run_app.log', 'w')
    last_ang = [999, 999, 999]

    # start main loop
    print('Starting')
    connection_manager.send_serial(State.STANDBY)
    while state_manager.get_state() > State.OFF:
        try:
            if state_manager.get_state() == State.CALIBRATE:
                cam_cal_success = False
                for attempt in range(2):
                    try:
                        # check connected to cam + serial
                        connection_manager.verify_connection()
                        _ = connection_manager.take_photos()
                        cam_cal_success = True
                        break
                    except StandbyTransition as st:
                        # if fails, reconnect cameras and retry
                        if attempt < 1:
                            post_msg(f'{st.message}; retrying', gui, False)
                            connection_manager.disconnect_cameras()
                            connection_manager.connect_cameras()
                if not cam_cal_success:
                    state_manager.standby()
                    post_msg('Calibration failed', gui, True)
                else:
                    # ensure it can find object
                    distance = 0
                    clear_location_history()
                    for i in range(5):
                        photos = connection_manager.take_photos()
                        center_l, angle_l = find_in_image(photos[0])
                        center_r, angle_r = find_in_image(photos[1])
                        ray_l = create_ray(*center_l, connection_manager.cam_res)
                        ray_r = create_ray(*center_r, connection_manager.cam_res)
                        vis.set_cam_rays(ray_l, ray_r)
                        location = locate_object(ray_l, ray_r)
                        store_location(monotonic(), location)
                        vis.set_obj(location)
                        verify_track(get_location_history())
                        distance += location[1]  # y coord; distance from arm front
                    # if object behind arm, swap cams
                    if distance < 0:
                        connection_manager.swap_cameras()
                    # check mechanical calibration
                    connection_manager.recv_serial()
                    connection_manager.send_serial(State.CALIBRATE)
                    connection_manager.recv_serial()
                    state_manager.ready()
                    connection_manager.send_serial(State.READY)
                    last_ang = [999, 999, 999]
                    clear_location_history()
                    post_msg('Calibration successful', gui, False)
            elif state_manager.get_state() > State.CALIBRATE:
                # monitor tracking
                photos = connection_manager.take_photos()
                center_l, angle_l = find_in_image(photos[0])
                center_r, angle_r = find_in_image(photos[1])
                ray_l = create_ray(*center_l, connection_manager.cam_res)
                ray_r = create_ray(*center_r, connection_manager.cam_res)
                vis.set_cam_rays(ray_l, ray_r)
                location = locate_object(ray_l, ray_r)
                store_location(monotonic(), location)
                vis.set_obj(location)
                verify_track(get_location_history())
                if state_manager.get_state() == State.READY:
                    connection_manager.recv_serial()
                    connection_manager.send_serial(State.READY)
                if state_manager.get_state() == State.ACTIVE:
                    # act upon tracking
                    arm_angles = pos_to_arm_angles(*simple_trajectory(location))
                    # limit to bounds
                    arm_angles = [
                        limit_joint_to_range(arm_angles[0]*R_TO_D, -60, 60),
                        limit_joint_to_range(arm_angles[1]*R_TO_D, -35, 55),
                        limit_joint_to_range(arm_angles[2]*R_TO_D, -180, 180),
                    ]
                    # reduce small movements by resending
                    if (
                            abs(last_ang[0] - arm_angles[0]) > 5 or
                            abs(last_ang[1] - arm_angles[1]) > 5 or
                            abs(last_ang[2] - arm_angles[2]) > 5
                    ):
                        connection_manager.recv_serial()
                        connection_manager.send_serial(State.ACTIVE, arm_angles)
                        last_ang = arm_angles
                        log_file.write(f'o {arm_angles[0]} {arm_angles[1]} {arm_angles[2]}\n')
                    else:
                        connection_manager.recv_serial()
                        connection_manager.send_serial(State.ACTIVE, last_ang)
                        log_file.write(f'r {last_ang[0]} {last_ang[1]} {last_ang[2]}\n')
            else:
                connection_manager.recv_serial()
                connection_manager.send_serial(State.STANDBY)
        except StandbyTransition as st:
            # handle error
            post_msg(st.message, gui, True)
            state_manager.error(st.message)
            connection_manager.send_serial(State.STANDBY)
        # handle state transitions
        current_state = state_manager.get_state()
        if last_state != state_manager.get_state():
            last_state = current_state
            gui.set_state(current_state)
            post_msg(f'State transition to {current_state.name}', gui, False)

    if gui.root.winfo_exists():
        gui.set_state(State.OFF)
    print('Cleaning up...')
    # cleanup
    connection_manager.send_serial(State.OFF)
    connection_manager.disconnect_arduino()
    connection_manager.disconnect_cameras()
    if gui.root.winfo_exists():
        gui.root.quit()
    log_file.close()
    print('Operation loop complete')
