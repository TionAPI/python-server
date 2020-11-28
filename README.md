# API server for Tion breezer
## Installation
```shell script
git clone https://github.com/TionAPI/python-server.git 
cd python-server
pip3 install -r requirements.txt
```
## Usage
```shell script
python3 main.py
curl -XGET 'http://127.0.0.1/s3/mac_of_you_breezer'
curl -XPOST 'http://127.0.0.1/s3/mac_of_you_breezer --data {"fan_speed": "1"}'
```
