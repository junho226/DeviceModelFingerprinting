# Prerequisite

- Pcap to txt conversion
  - tshark
  - Python3

- Generate fingerprint
  - Python2.7
  
# Wireshark setting

For pcap parsing, DLT_USER setting is required.
- Edit > Preferences > Protocols > DLT_USER

|DLT|Payload protocol|
|---|---|
|147|mac-lte-framed|
|148|nas-eps|
|149|udp|
|150|s1ap|


# How to run

Convert pcap files to txt in directory "pcaps" for feature vector generation
```sh
python3 pcap2txt.py -d pcaps
```

Generate single feature vector with a file "Galaxy_S5.txt":
```sh
python msg_parser.py -f Galaxy_S5.txt
```

Generate feature vectors with a directory "Galaxy":
```sh
python msg_parser.py -d Galaxy
```

# BibTex

```bibtex
@inproceedings{oh2023preventing,
 title={Preventing SIM Box Fraud Using Device Model Fingerprinting},
 author={Oh, Beomseok and Ahn, Junho and Bae, Sangwook and Son, Mincheol and Lee, Yonghwa and Kang, Minsuk and Kim, Yongdae},
 booktitle={Network and Distributed Systems Security (NDSS) Symposium},
 year={2023}
}
```
