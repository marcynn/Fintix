# Fintix
> I'll be sharing the deployed web app soon so that anyone can access it without having to download it locally. 

## Description
Quantitative analytics dash application for comparing investment strategies and assets. 

It is built on top of [@ranaroussi's](https://github.com/ranaroussi) [quantstats](https://github.com/ranaroussi/quantstats) library and provides an easy and interactive experience for investment analytics. 

## Usage
Upload csv file or download csv data directly from Yahoo Finance within the app. 

The data template format is a date column called "Date" followed by assets columns containing asset prices.

> Upload and submit once. Adjust parameters on the fly. 

![image](https://user-images.githubusercontent.com/85497151/232108688-53f2ccbf-c340-45fe-886a-f29bccc197cf.png)

Download from Yahoo Finance

![image](https://user-images.githubusercontent.com/85497151/232109247-29ec6a3e-251f-4d94-9e35-73d6b9af66cc.png)

## Modules
### Compare
![image](https://user-images.githubusercontent.com/85497151/232109489-b3e27e4c-b2dd-4411-9165-c0ab99f7de95.png)

### Returns
![image](https://user-images.githubusercontent.com/85497151/232109535-9533f4f1-3547-4a9f-a650-99d60824ffe1.png)

### Benchmark
![image](https://user-images.githubusercontent.com/85497151/232109616-a9ffd11a-fd1f-4808-9dc7-76783417ed5a.png)

### Rolling
![image](https://user-images.githubusercontent.com/85497151/232109669-9c72d70d-da99-4d58-8e15-4f8fb60d3793.png)

## Installation
Install Python if you don't have it already installed. Plenty of resources online to do so.
### Pre-requisites
```bash
pip install -r requirements.txt
```
> Consider creating a virual enviornment before installing requirements. 

### Run App
```bash
python app.py
```
## Other
### License
Fintix is distributed under MIT license. Refer to [LICENSE](https://github.com/marcynn/Fintix/blob/main/LICENSE) file for more details.
### Issues
If you spot any bugs, typos, or if you have any question, please open an [issue](https://github.com/marcynn/Fintix/issues).
###Contributions
Submit pull requests or reach out to me directly to add additional features.
