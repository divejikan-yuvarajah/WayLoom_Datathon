from __future__ import annotations

import pandas as pd
import pytest

from src.task1.historical_features import Task1HistoricalFeatureTransformer


def _hist_fixture() -> tuple[pd.DataFrame, pd.Series, pd.Series]:
    X = pd.DataFrame(
        [
            {"delivery_id": "D3", "date": "2026-01-02", "outlet_id": "O1", "brand": "Fresh", "dock_type": "rear_dock"},
            {"delivery_id": "D1", "date": "2026-01-01", "outlet_id": "O1", "brand": "Fresh", "dock_type": "rear_dock"},
            {"delivery_id": "D2", "date": "2026-01-01", "outlet_id": "O2", "brand": "Fresh", "dock_type": "street"},
            {"delivery_id": "D4", "date": "2026-01-03", "outlet_id": "O3", "brand": "Style", "dock_type": "street"},
        ]
    )
    y_service = pd.Series([30.0, 10.0, 20.0, 40.0], name="service_minutes")
    y_late = pd.Series([1, 0, 1, 0], name="late_flag")
    return X, y_service, y_late


def test_dt119_current_same_day_future_excluded() -> None:
    X, y_service, y_late = _hist_fixture()
    tr = Task1HistoricalFeatureTransformer(date_col="date")
    out = tr.fit_transform_training_chronological(X[["date", "outlet_id", "brand", "dock_type"]], y_service, y_late)

    # Same-day exclusion: the first date has no prior target history, so
    # cold-start historical features remain missing rather than seeing future data.
    i1 = X.index[X["delivery_id"] == "D1"][0]
    i2 = X.index[X["delivery_id"] == "D2"][0]
    assert pd.isna(out.loc[i1, "outlet_prior_service_median"])
    assert pd.isna(out.loc[i2, "brand_prior_late_rate"])

    # Row on 2026-01-02 can use prior day only, not future day 2026-01-03.
    i3 = X.index[X["delivery_id"] == "D3"][0]
    assert out.loc[i3, "outlet_prior_service_median"] == pytest.approx(10.0)


def test_dt119_fit_transform_validation_scope_and_unseen_fallback() -> None:
    X, y_service, y_late = _hist_fixture()
    train = X[X["date"] <= "2026-01-02"].copy()
    y_s_train = y_service.loc[train.index]
    y_l_train = y_late.loc[train.index]

    val = pd.DataFrame(
        [
            {"date": "2026-01-04", "outlet_id": "O99", "brand": "Fresh", "dock_type": "rear_dock"},
            {"date": "2026-01-04", "outlet_id": "O2", "brand": "Fresh", "dock_type": "street"},
        ]
    )
    tr = Task1HistoricalFeatureTransformer(date_col="date").fit(
        train[["date", "outlet_id", "brand", "dock_type"]], y_s_train, y_l_train
    )
    val_out = tr.transform(val[["outlet_id", "brand", "dock_type"]])
    assert "outlet_prior_service_median" in val_out.columns
    # unseen outlet should fallback to brand+dock or brand/global, not NaN
    assert pd.notna(val_out.loc[0, "outlet_prior_service_median"])


def test_dt119_deterministic_under_shuffle() -> None:
    X, y_service, y_late = _hist_fixture()
    tr = Task1HistoricalFeatureTransformer(date_col="date")
    out1 = tr.fit_transform_training_chronological(X[["date", "outlet_id", "brand", "dock_type"]], y_service, y_late)

    shuffled = X.sample(frac=1.0, random_state=7)
    ys = y_service.loc[shuffled.index]
    yl = y_late.loc[shuffled.index]
    out2 = tr.fit_transform_training_chronological(shuffled[["date", "outlet_id", "brand", "dock_type"]], ys, yl)
    # Compare after restoring original index order
    out2 = out2.reindex(out1.index)
    pd.testing.assert_frame_equal(out1.sort_index(), out2.sort_index())


def test_dt119_running_median_is_exact_across_even_and_odd_history() -> None:
    X = pd.DataFrame(
        {
            "date": ["2026-01-01", "2026-01-02", "2026-01-03", "2026-01-04"],
            "outlet_id": ["O1"] * 4,
            "brand": ["Fresh"] * 4,
            "dock_type": ["rear_dock"] * 4,
        }
    )
    service = pd.Series([40.0, 10.0, 30.0, 20.0])
    late = pd.Series([0, 1, 1, 0])

    out = Task1HistoricalFeatureTransformer(date_col="date").fit_transform_training_chronological(
        X, service, late
    )

    assert out["outlet_prior_service_median"].tolist()[1:] == pytest.approx(
        [40.0, 25.0, 30.0]
    )
    assert out["outlet_prior_late_rate"].tolist()[1:] == pytest.approx(
        [0.0, 0.5, 2.0 / 3.0]
    )
