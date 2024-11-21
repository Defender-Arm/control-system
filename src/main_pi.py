from service.connection.linux import ConnectionFromLinux
from service.handler.log_accel import LogAccHandler


def main():
    handler = LogAccHandler()
    connection = ConnectionFromLinux(handler, run_time=10)
    connection.connect()
    return


if __name__ == "__main__":
    main()
