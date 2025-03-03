from datetime import datetime
from time import monotonic

from src.backend.error.standby_transition import StandbyTransition
from src.backend.external_management.connections import Ext
from src.backend.sensor_fusion.tracking import (
    find_in_image, create_ray, locate_object, store_location, get_location_history
)
from src.backend.state_management.error_checker import verify_track
from src.backend.state_management.state_manager import Manager, State
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
                state_manager.ready()
                post_msg('Calibration successful', gui, False)
            elif state_manager.get_state() > State.CALIBRATE:
                # monitor tracking
                photos = connection_manager.take_photos()
                center_l, angle_l = find_in_image(photos[0])
                center_r, angle_r = find_in_image(photos[1])
                ray_l = create_ray(*center_l)
                ray_r = create_ray(*center_r)
                vis.set_cam_rays(ray_l, ray_r)
                location = locate_object(ray_l, ray_r)
                store_location(monotonic(), location)
                vis.set_obj(location)
                # verify_track(get_location_history())
                if state_manager.get_state() == State.ACTIVE:
                    # act upon tracking
                    pass
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

    gui.set_state(State.OFF)
    print('Cleaning up...')
    # cleanup
    connection_manager.disconnect_cameras()
    print('Operation loop complete')
