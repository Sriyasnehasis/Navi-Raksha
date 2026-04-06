# Model Comparison — NaviRaksha ETA Prediction

| Model | Val MAE (min) | Test MAE (min) | Target | Status |
|-------|--------------|----------------|-------- |--------|
| Random Forest | 0.406 | 0.427 | < 3.0 |  Passed |
| LSTM Baseline | 0.313 | 0.346 | < 3.9 |  Passed |
| GNN (planned) | TBD   | TBD   | < 3.0 |  Week 3 |

## Notes
- RF trained on 350 samples, 21 features
- LSTM: 64 hidden units, 50 epochs, batch size 32
- GNN will use graph structure of Navi Mumbai road network