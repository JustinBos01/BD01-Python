from time import sleep

from pysphero.utils import toy_scanner


def main():
    with toy_scanner() as sphero:
        sphero.power.wake()
        sleep(2)
        sphero.power.enter_soft_sleep()


if __name__ == '__main__':
    main()
