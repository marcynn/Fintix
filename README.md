# Fintix
> Currently deployed on fintix.live 
> - Note -> Locally running the app results in better performance.

## Description
Fintix started as a quantitative analytics dash application for comparing investment strategies and assets. It is now branching to become an open source investment analytics and research platform written in Python. 

![image](https://user-images.githubusercontent.com/85497151/236621552-74824fc3-8d30-42a5-8c7f-a01f06705f64.png)

## Usage
Go to the module that you want to explore. If a module requires data upload, you can either upload csv file or download csv data directly from Yahoo Finance within the app. 

The data template format is a date column called "Date" followed by assets columns containing asset prices.

> Upload csv and submit once. Adjust parameters on the fly. 
> - Parameters are initialized to default values.
> - Adjust start and end dates to analyze various timeframes. There's a lookback option to swiftly filter for dates and scenarios such as the Covid crash.
> - Adjust other parameters such as rolling window, periods per year for annualized metrics, risk free rate, main and benchmark assets for one to one comparison, etc.
> - Filter loaded asset universe to the assets that you want to analyze. For example, load 15 assets, filter for 4.

![image](https://user-images.githubusercontent.com/85497151/236621737-7aa324be-6d14-4686-8fd7-c416b0d5c739.png)

![image](https://user-images.githubusercontent.com/85497151/236621754-75c054a0-a9dd-4ab6-8ba5-eee433a703b7.png)


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
### Acknowledgment
Fintix uses [@ranaroussi's](https://github.com/ranaroussi) [quantstats](https://github.com/ranaroussi/quantstats) library for most metrics. Quantstats made it a breeze to build the app. 
### License
Fintix is distributed under MIT license. Refer to [LICENSE](https://github.com/marcynn/Fintix/blob/main/LICENSE) file for more details.
### Issues
If you spot any bugs, typos, or if you have any questions, please open an [issue](https://github.com/marcynn/Fintix/issues).
### Contributions
Submit pull requests or reach out to me directly to add additional features.
