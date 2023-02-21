import os
import argparse


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-d", "--dir", help="Directory of pcap files")
    args = argparser.parse_args()
    
    pcap_dir = args.dir
    files = os.listdir(pcap_dir)
    os.mkdir(pcap_dir+'_txt')
    for file in files:
        txt = file.replace('pcap','txt')
        command = 'tshark -r ./'+pcap_dir+'/{} -V -T text > ./'.format(file)+pcap_dir+'_txt/{}'.format(txt)
        os.popen(command)


if __name__ == '__main__':
    main()