# Function-Simulator

Function-Simulator is a simulator to simulate the invocation of serverless functions. It uses azure2019 trace as input,
and the simulation interval is one minute.

## Getting Started

```
git clone https://github.com/JBinin/Function-Simulator.git
cd Function-Simulator
python3 -m pip install --upgrade pip
pip install -r requirements.txt
python3 main.py
```

## Test

```
cd Function-Simulator
python3 test.py
```