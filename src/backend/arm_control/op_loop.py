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


def operation_loop(state_manager: Manager, connection_manager: Ext, gui: Gui, vis: Graph):
    # setup instances
    print('Preparing managers...')

    # start main loop
    print('Starting')
    while state_manager.get_state() > State.OFF:
        try:
            if state_manager.get_state() == State.CALIBRATE:
                # predefined checks
                print('Calibrating...')
                # connection_manager.verify_connection()
                state_manager.ready()
            if state_manager.get_state() > State.CALIBRATE:
                # monitor tracking
                # photos = connection_manager.take_photos()
                # center_l, angle_l = find_in_image(photos[0])
                # center_r, angle_r = find_in_image(photos[1])
                # ray_l = create_ray(*center_l)
                # ray_r = create_ray(*center_r)
                # vis.set_cam_rays()
                # location = locate_object(ray_l, ray_r)
                # store_location(monotonic(), location)
                # vis.set_obj(location)
                # verify_track(get_location_history())
                if state_manager.get_state() == State.ACTIVE:
                    # act upon tracking
                    pass
        except StandbyTransition as st:
            print(f'Error: {st.message}')
            state_manager.error(st.message)
        gui.set_logs([f'{e[0]}: {e[1]}' for e in state_manager.get_errors()])
        gui.set_state(state_manager.get_state())

    gui.set_state(State.OFF)
    print('Cleaning up...')
    # cleanup
    connection_manager.disconnect_cameras()
    print('Operation loop complete')
