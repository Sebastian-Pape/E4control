# -*- coding: utf-8 -*-

import os
import sys
import argparse
import time
import termios, tty

from threading import Thread

from .. import utils as sh

# arg parser
parser = argparse.ArgumentParser()
parser.add_argument('config', help='config file')
parser.add_argument('-l', '--logfile', help='potential logfile')


class pressedKeyThread(Thread):
    pressed_key = ''

    def run(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
     
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        self.pressed_key = ch
        print('"{}" has been pressed.'.format(self.pressed_key))


def print(string):
    sys.stdout.write(string+'\r\n')

def main():
    args = parser.parse_args()

    # read configfile
    config_devices = sh.read_testbeamDCS_config(args.config)

    # create setting query
    sh.show_testbeamDCS_device_list(config_devices)

    # connection
    devices = sh.connect_testbeamDCS_devices(config_devices)

    # logfile
    if args.logfile:
        checktxtfile = (args.logfile + '.txt')
        if os.path.isfile(checktxtfile):
            sys.exit('logfile ' + args.logfile + ' already exists!')
        fw = sh.new_txt_file(args.logfile)
        header = ['time']
        d_names = []
        for i in config_devices:
            d_names.append('|')
            d_names.append(i[0])
            d_names.append(i[1])
            d_names.append('|')
        for i in devices:
            header = header + (i.output(show=False)[0])
        sh.write_line(fw, d_names)
        sh.write_line(fw, header)

    starttime = time.time()

    while True:
        key_thread = pressedKeyThread()
        key_thread.start()
        while key_thread.is_alive():
            values = [str(time.time())]
            print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
            timestamp = (time.time()-starttime) / 60
            h, s = divmod(timestamp, 1)
            # timestamp = time.strftime('%a, %d %b %Y %H:%M:%S ', time.localtime())
            print(' \033[35m CONTROL CENTER \t ' + 'runtime: %.0f min %.0f s \033[0m' % (h, s*60))
            print('-----------------------------------------------------')
            for d in devices:
                try:
                    h, v = d.output()
                    values += v
                    print('-----------------------------------------------------')
                except:
                    h = []
                    v = []
                    h, v = d.output()
                    values += v
                    print('-----------------------------------------------------')
            if args.logfile:
                sh.write_line(fw, values)
            time.sleep(1)
            print('press c (=CHANGE PARAMETER) or q (=QUIT) and ENTER')
            print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
            if key_thread.is_alive():
                time.sleep(10)
            print('')

        key_thread.join()
        key = key_thread.pressed_key
        print('Interpreting "{}" key...'.format(key_thread.pressed_key))

        if key == 'q':
            print('Quitting...')
            break

        if key == 'c':
            print('List of active Devices:')
            print('0: Continue dcs mode without changes')
            for i in range(len(config_devices)):
                print('%i: %s' % (i+1, config_devices[i][1]))
            x = int(input('Choose the number of a Device:'))
            if (x-1) in range(len(config_devices)):
                devices[x-1].interaction()
            else:
                continue
        else:
            print('Cannot handle this key. Continuing.')
            time.sleep(1)

    # print(threadKey.is_alive())
    for d in devices:
        d.close()
    if args.logfile:
        sh.close_txt_file(fw)


if __name__ == '__main__':
    main()
