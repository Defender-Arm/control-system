from src.backend.error.standby_transition import StandbyTransition
from src.backend.sensor_fusion.tracking import (
    find_in_image, create_ray, locate_object, store_location, get_location_history
)
from src.backend.state_management.state_manager import Manager, State

if __name__ == '__main__':
    # setup instances
    print('Preparing managers...')
    state_manager = Manager()
    connection_manager = None
    #make display

    # start main loop
    print('Starting')
    while state_manager.get_state() > State.OFF:
        try:
            if state_manager.get_state() == State.CALIBRATE:
                # predefined checks
                print('Calibrating...')
                #calibrate module
                state_manager.ready()
            if state_manager.get_state() > State.CALIBRATE:
                # monitor tracking
                #photos
                #find
                #ray
                #locate
                #error check
                if state_manager.get_state() == State.ACTIVE:
                    # act upon tracking
                    pass
        except StandbyTransition as st:
            print(f'Error: {st.message}')
            state_manager.error(st.message)


    # cleanup
    #connection_manager.close_all()