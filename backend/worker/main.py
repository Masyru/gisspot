from backend.worker.services import create_worker
from backend.worker.settings import WORKER_TYPES

if __name__ == '__main__':
    # file_1 = "C:\\Users\\bader\\PycharmProjects\\gisspot\\backend\\database\\data\\pro\\NOAA_15_20210301_213305.f.pro"
    # file_2 = "C:\\Users\\bader\\PycharmProjects\\gisspot\\backend\\database\\data\\pro\\NOAA_15_20210301_231345.f.pro"
    # points = ((30.0, 130.0),)
    # deltatime = 6039
    # big_worker(file_1, file_2, points=points, deltatime=deltatime, window_size=(31, 31), vicinity_size=(80, 80))
    create_worker(WORKER_TYPES)

