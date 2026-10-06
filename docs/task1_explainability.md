# Task 1 Explainability

## What is explained

This summary describes the frozen `catboost` service-time model and the frozen `catboost` lateness classifier. Explanations use a deterministic local sample of 2000 Task 1 inference rows and the exact saved feature schema. No model was retrained or changed.

## Service-time model

The highest global mean-absolute-SHAP features were `outlet_prior_service_median`, `festival_ramp`, `order_volume_m3`, `monsoon`, `order_weight_kg`. Mean absolute SHAP measures attribution strength; it does not establish a universal direction. The private `SERVICE_EXAMPLE_A` record reconstructs the raw model prediction before the frozen service post-processing policy.

## Late-risk model

The highest global mean-absolute-SHAP features were `planned_slack_to_close_min`, `monsoon`, `outlet_prior_late_rate`, `planned_arrival_cos`, `prior_planned_units`. Lateness SHAP values are reported in `raw_margin_log_odds` for the base classifier and must not be read as probability-point changes. The private `LATE_EXAMPLE_A` record separately verifies the bridge from the base classifier probability through calibration `raw` to the submitted probability.

## Business interpretation

“Driver” means a model driver or predictive association, not a causal driver. Feature rankings describe how the frozen models use the observed prediction-time information. Direction can be mixed or interaction-dependent, and operational actionability cannot be inferred from rank alone.

## Limitations

SHAP attribution can be distributed among correlated or redundant features. Feature importance is model-specific. A highly ranked feature is not necessarily actionable, and a low-ranked feature is not necessarily operationally unimportant. Categorical effects can depend on interactions and context.

These explanations describe how the trained model uses observed features. They reflect model associations and attribution, not causal effects.
