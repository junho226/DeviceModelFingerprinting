# Description

The paper proposes a new approach to mitigate SIM box fraud, which involves preventing SIM box devices from using cellular networks. They propose a simple access control logic that uses precise fingerprinting of device models and types to detect unauthorized SIM box use. They demonstrate that fingerprints constructed from network-layer auxiliary information are mostly distinct among smartphones and can be used to prevent the majority of illegal SIM boxes from making unauthorized voice calls. This proposal is the first practical and reliable unauthorized cellular device model detection scheme and simplifies the mitigation against SIM box fraud.

# Prerequisite

- Pcap to txt conversion
  - tshark
  - Python3

- Generate fingerprint
  - Python2.7

# How to run

Convert pcap files to txt in directory "pcaps" for feature vector generation
```sh
python3 pcap2txt -d pcaps
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
