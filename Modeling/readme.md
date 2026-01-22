# T1D Dataset preprocessing and Modeling using XGBoostRegressor Model

## Intro:


After many attempts with DeepNN and Timeseries based approaches such as:
- LSTM
- Temporal Convolutional Network
- Gru
- Simple RNN

Which all reached their limit pretty fast due to the length of the data especially post pre proccessing which left a low number of rows suitable for Training these types of models. 

As a result, I switched to a classical ML Regressor, specifically, the XGBoostRegressor that instantly provide better Accuracies and better feature useage with basic prerocessing and Fine tuning.

## Process
First things first, we start with better pre-processing that Has the Model in mind extracting rolling mean, rolling std. dev., lagged features, IOB*, COB*, Day/Night and other Time based features info for Dawn phenomenon detection, etc... Right after that we start Training on the ```XGBoostRegressor``` regression model with the following model parameters:

### Model parameters
```json
{
    n_estimators=1000,       
    max_depth=6,             
    learning_rate=0.05,      
    subsample=0.8,           
    colsample_bytree=0.8,    
    min_child_weight=3,      
    gamma=0.1,               
    reg_alpha=0.1,           
    reg_lambda=1.0,          
    random_state=42,
    n_jobs=-1,
    early_stopping_rounds=50 
}
```
### Regularization 
Both L1 and L2 Regularization where used which actually left us with Test accuracies less than Training ones (R^2) 

Note: Difference between training and test accuracies was within limits ofc which where never more than 0.1 in all training cases across all horizons.

### Most Important Featurs:

(Actuall bard graphs will be compiled and uploaded soon)

Most Important features actually differ across different horizon which actually reflects real behaviour where short term prediction rely heavily on glucose readings the past hour or so while predictions across longer horizons (60-90 minutes) rely more on Exercise, IOB, COB, Time of Day, etc... which again, reflects expected behaviour.


### Accuracies:
After Training and testing based on all the previously mentioned, we were left with the following **R2 Test** accuracies

| Horizon Length | Accuracy |
| -------------- | -------- |
| 30 minute | 93.7% R2 |
| 45 minute | 94.3% R2 |
| 60 minute | 94.7% R2 |
| 90 minute | 84.7% R2 |

