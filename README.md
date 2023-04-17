# Fintix
> Currently deployed on fintix.live 
> - Note -> Locally running the app results in better performance.

## Description
Quantitative analytics dash application for comparing investment strategies and assets. 

It is built on top of [@ranaroussi's](https://github.com/ranaroussi) [quantstats](https://github.com/ranaroussi/quantstats) library and provides an easy and interactive experience for investment analytics. 

## Usage
Upload csv file or download csv data directly from Yahoo Finance within the app. 

The data template format is a date column called "Date" followed by assets columns containing asset prices.

> Upload csv and submit once. Adjust parameters on the fly. 
> - Parameters are initialized to default values.
> - Adjust start and end dates to swiftly analyze various timeframes.
> - Adjust other parameters such as rolling window, periods per year for annualized metrics, risk free rate, main and benchmark assets for one to one comparison, etc.
> - Filter loaded asset universe to the assets that you want to analyze. For example, load 15 assets, filter for 4.

![image](https://user-images.githubusercontent.com/85497151/232431388-fdfc1246-fa67-47fd-9a4b-ab8872ba1cc8.png)

Download from Yahoo Finance

![image](https://user-images.githubusercontent.com/85497151/232432298-862264b0-b71e-4372-b74b-6453c01e0215.png)

## Modules
### Compare
![image](https://user-images.githubusercontent.com/85497151/232109489-b3e27e4c-b2dd-4411-9165-c0ab99f7de95.png)

### Returns
![image](https://user-images.githubusercontent.com/85497151/232109535-9533f4f1-3547-4a9f-a650-99d60824ffe1.png)

### Benchmark
![image](https://user-images.githubusercontent.com/85497151/232109616-a9ffd11a-fd1f-4808-9dc7-76783417ed5a.png)

### Rolling
![image](https://user-images.githubusercontent.com/85497151/232203347-6673b881-3350-455a-87eb-dde947becab7.png)

## Installation
1. Install Python if you don't have it already installed. Plenty of resources online to do so.

2. Clone repository to your local environment
```bash
git clone https://github.com/marcynn/Fintix.git
```
3. Change directory to where you cloned the repo

4. Install requirements
```bash
pip install -r requirements.txt
```
> Consider creating a virual enviornment before installing requirements. 

5. Run App
```bash
python app.py
```
## Other
### License
Fintix is distributed under MIT license. Refer to [LICENSE](https://github.com/marcynn/Fintix/blob/main/LICENSE) file for more details.
### Issues
If you spot any bugs, typos, or if you have any questions, please open an [issue](https://github.com/marcynn/Fintix/issues).
### Contributions
Submit pull requests or reach out to me directly to add additional features.
