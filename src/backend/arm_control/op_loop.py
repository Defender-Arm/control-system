from datetime import datetime
from time import monotonic

from src.backend.error.standby_transition import StandbyTransition
from src.backend.external_management.connections import Ext
from src.backend.sensor_fusion.tracking import (
    find_in_image, create_ray, locate_object, store_location, get_location_history, clear_location_history
)
from src.backend.state_management.error_checker import verify_track
from src.backend.state_management.state_manager import Manager, State
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


def operation_loop(state_manager: Manager, connection_manager: Ext, gui: Gui, vis: Graph):
    # setup instances
    print('Preparing managers...')
    last_state = None
    log_file = open('run_app.log', 'w')
    last = 0

    # start main loop
    print('Starting')
    while state_manager.get_state() > State.OFF:
        try:
            if state_manager.get_state() == State.CALIBRATE:
                # predefined checks
                try:
                    connection_manager.verify_connection()
                    _ = connection_manager.take_photos()
                except StandbyTransition as st:
                    post_msg(f'{st.message}; reconnecting', gui, False)
                    connection_manager.disconnect_cameras()
                    connection_manager.connect_cameras()
                    connection_manager.verify_connection()
                last_ang = [999, 999, 999]
                clear_location_history()
                state_manager.ready()
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
                if state_manager.get_state() == State.ACTIVE:
                    # act upon tracking
                    arm_angles = pos_to_arm_angles(*location)
                    arm_angles = [angle*R_TO_D for angle in arm_angles]
                    if arm_angles[0] < -60:
                        print(f'arm_angles[0] increased from {arm_angles[0]} to -60')
                        arm_angles[0] = -60
                    if arm_angles[0] > 60:
                        print(f'arm_angles[0] decreased from {arm_angles[0]} to 60')
                        arm_angles[0] = 60
                    if arm_angles[1] < -45:
                        print(f'arm_angles[1] increased from {arm_angles[1]} to -45')
                        arm_angles[1] = -45
                    if arm_angles[1] > 45:
                        print(f'arm_angles[1] decreased from {arm_angles[1]} to 45')
                        arm_angles[1] = 45
                    if abs(arm_angles[2]) > 180:
                        print(f'arm_angles[2] changed from {arm_angles[2]} to 180')
                        arm_angles[2] = 180
                    if last + 0.2 < monotonic():
                        if (
                                abs(last_ang[0] - arm_angles[0]) > 5 or
                                abs(last_ang[1] - arm_angles[1]) > 5 or
                                abs(last_ang[2] - arm_angles[2]) > 5
                        ):
                            print(f'target is {int(arm_angles[0])} {int(arm_angles[1])} {int(arm_angles[2])}')
                            last = monotonic()
                            last_ang = arm_angles
                            log_file.write(f'o {int(arm_angles[0])} {int(arm_angles[1])} {int(arm_angles[2])}\n')
                        else:
                            last = monotonic()
                            print(f'RESEND target is {int(last_ang[0])} {-int(last_ang[1])} {int(last_ang[2])}')
                            log_file.write(f'r {int(last_ang[0])} {int(last_ang[1])} {int(last_ang[2])}\n')
                    else:
                        log_file.write(f'x {int(arm_angles[0])} {int(arm_angles[1])} {int(arm_angles[2])}\n')
        except StandbyTransition as st:
            # handle error
            post_msg(st.message, gui, True)
            state_manager.error(st.message)
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
    connection_manager.disconnect_cameras()
    if gui.root.winfo_exists():
        gui.root.quit()
    log_file.close()
    print('Operation loop complete')
