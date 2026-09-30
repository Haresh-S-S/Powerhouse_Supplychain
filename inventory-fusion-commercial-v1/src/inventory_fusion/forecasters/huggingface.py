from __future__ import annotations

import gc
from collections.abc import Mapping
from pathlib import Path

import numpy as np

from inventory_fusion.forecasters.base import Forecaster, validate_future_dates
from inventory_fusion.types import DEFAULT_QUANTILES, Forecast, TimeSeries


class ModelDependencyError(RuntimeError):
    pass


def _device_name(requested: str) -> str:
    try:
        import torch
    except ImportError as exc:
        raise ModelDependencyError("PyTorch is required for Hugging Face model adapters") from exc
    if requested.startswith("cuda") and not torch.cuda.is_available():
        raise ModelDependencyError(
            "CUDA was requested but torch.cuda.is_available() is false; install a CUDA PyTorch build"
        )
    return requested


class TTMForecaster(Forecaster):
    """IBM Granite TTM R2.1 daily point forecast with residual quantile calibration."""

    MODEL_ID = "ibm-granite/granite-timeseries-ttm-r2"
    REVISION = "caa1eb3d16f053859d81952a1f387d6aeb670076"

    def __init__(
        self,
        model_path: str | Path = "models/ttm-r2.1-512-48",
        *,
        device: str = "cuda",
        context_length: int = 512,
        max_horizon: int = 48,
    ) -> None:
        self.model_path = Path(model_path)
        self.device = _device_name(device)
        self.context_length = context_length
        self.max_horizon = max_horizon
        self.name = "ttm_r2_1_daily"
        self._model = None

    def _load(self):
        if self._model is not None:
            return self._model
        try:
            from tsfm_public.toolkit.get_model import get_model
        except ImportError as exc:
            raise ModelDependencyError("Install inventory-fusion[ttm]") from exc
        if self.model_path.exists():
            # granite-tsfm 0.3.8 get_model() assumes a non-null revision even for
            # local directories. Load the exact downloaded checkpoint directly.
            from tsfm_public.models.tinytimemixer.modeling_tinytimemixer import (
                TinyTimeMixerForPrediction,
            )

            self._model = TinyTimeMixerForPrediction.from_pretrained(
                str(self.model_path), prediction_filter_length=self.max_horizon
            )
        else:
            self._model = get_model(
                model_path=self.MODEL_ID,
                context_length=self.context_length,
                prediction_length=self.max_horizon,
                model_revision=self.REVISION,
            )
        self._model = self._model.to(self.device).eval()
        return self._model

    def predict(
        self,
        history: TimeSeries,
        horizon: int,
        *,
        future_dates: np.ndarray | None = None,
        future_covariates: Mapping[str, np.ndarray] | None = None,
        quantiles: tuple[float, ...] = DEFAULT_QUANTILES,
    ) -> Forecast:
        del future_dates, future_covariates
        if horizon > self.max_horizon:
            raise ValueError(f"TTM adapter supports at most {self.max_horizon} steps per call")
        import torch

        values = history.values[-self.context_length :]
        if len(values) < self.context_length:
            values = np.pad(values, (self.context_length - len(values), 0), mode="edge")
        tensor = torch.as_tensor(values, dtype=torch.float32, device=self.device).reshape(
            1, self.context_length, 1
        )
        with torch.inference_mode():
            output = self._load()(
                past_values=tensor,
                freq_token=torch.tensor([8], device=self.device),
                return_loss=False,
            )
        point = output.prediction_outputs[0, :horizon, 0].detach().float().cpu().numpy()
        residuals = (
            history.values[7:] - history.values[:-7]
            if len(history.values) > 14
            else history.values - np.mean(history.values)
        )
        return Forecast.from_point(
            self.name,
            history.sku,
            point,
            residuals,
            quantiles,
            metadata={"model_id": self.MODEL_ID, "revision": self.REVISION},
        )

    def close(self) -> None:
        self._model = None
        gc.collect()
        try:
            import torch

            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass


class Chronos2Forecaster(Forecaster):
    """Amazon Chronos-2 quantile model with optional known-future covariates."""

    MODEL_ID = "amazon/chronos-2"
    REVISION = "29ec3766d36d6f73f0696f85560a422f50e8498c"

    def __init__(
        self,
        model_path: str | Path = "models/chronos-2",
        *,
        device: str = "cuda",
        context_length: int = 512,
    ) -> None:
        self.model_path = Path(model_path)
        self.device = _device_name(device)
        self.context_length = context_length
        self.name = "chronos_2"
        self._pipeline = None

    def _load(self):
        if self._pipeline is not None:
            return self._pipeline
        try:
            import torch
            from chronos import Chronos2Pipeline
        except ImportError as exc:
            raise ModelDependencyError("Install inventory-fusion[chronos]") from exc
        source = str(self.model_path) if self.model_path.exists() else self.MODEL_ID
        kwargs = {"device_map": self.device, "dtype": torch.float32}
        if not self.model_path.exists():
            kwargs["revision"] = self.REVISION
        self._pipeline = Chronos2Pipeline.from_pretrained(source, **kwargs)
        return self._pipeline

    def predict(
        self,
        history: TimeSeries,
        horizon: int,
        *,
        future_dates: np.ndarray | None = None,
        future_covariates: Mapping[str, np.ndarray] | None = None,
        quantiles: tuple[float, ...] = DEFAULT_QUANTILES,
    ) -> Forecast:
        future_dates = validate_future_dates(history, horizon, future_dates)
        future_covariates = future_covariates or {}
        known_covariates = sorted(set(history.covariates) & set(future_covariates))
        pipeline = self._load()
        if known_covariates:
            import pandas as pd

            context_length = min(self.context_length, len(history.values))
            frame = pd.DataFrame(
                {
                    "item_id": history.sku,
                    "timestamp": pd.to_datetime(history.dates[-context_length:]),
                    "target": history.values[-context_length:],
                }
            )
            future = pd.DataFrame(
                {"item_id": history.sku, "timestamp": pd.to_datetime(future_dates)}
            )
            for name in known_covariates:
                frame[name] = np.asarray(history.covariates[name][-context_length:], dtype=float)
                values = np.asarray(future_covariates[name], dtype=float)
                if len(values) != horizon:
                    raise ValueError(f"future covariate {name!r} must match horizon")
                future[name] = values
            output = pipeline.predict_df(
                frame,
                future_df=future,
                prediction_length=horizon,
                quantile_levels=list(quantiles),
                batch_size=1,
                context_length=context_length,
            )
            values = {q: output[str(q)].to_numpy(dtype=float) for q in quantiles}
        else:
            quantile_predictions, _ = pipeline.predict_quantiles(
                [history.values[-self.context_length :].astype(np.float32)],
                prediction_length=horizon,
                quantile_levels=list(quantiles),
                batch_size=1,
                context_length=min(self.context_length, len(history.values)),
            )
            array = quantile_predictions[0].detach().float().cpu().numpy()
            if array.ndim == 3 and array.shape[0] == 1:
                array = array[0]
            values = {q: array[:, index] for index, q in enumerate(quantiles)}
        return Forecast(
            model_name=self.name,
            sku=history.sku,
            values=values,
            metadata={"model_id": self.MODEL_ID, "revision": self.REVISION},
        )

    def fit_lora(
        self,
        training_inputs,
        *,
        prediction_length: int,
        validation_inputs=None,
        output_dir: str | Path = "outputs/chronos-lora",
        num_steps: int = 500,
        batch_size: int = 4,
        learning_rate: float = 1e-5,
    ) -> None:
        self._pipeline = self._load().fit(
            inputs=training_inputs,
            validation_inputs=validation_inputs,
            prediction_length=prediction_length,
            finetune_mode="lora",
            context_length=self.context_length,
            learning_rate=learning_rate,
            num_steps=num_steps,
            batch_size=batch_size,
            output_dir=output_dir,
            disable_data_parallel=True,
            fp16=True,
            gradient_accumulation_steps=4,
        )

    def close(self) -> None:
        self._pipeline = None
        gc.collect()
        try:
            import torch

            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass


class TimesFMForecaster(Forecaster):
    """Google TimesFM 2.5 long-context point and continuous-quantile adapter."""

    MODEL_ID = "google/timesfm-2.5-200m-pytorch"
    REVISION = "1d952420fba87f3c6dee4f240de0f1a0fbc790e3"
    NATIVE_QUANTILES = tuple(i / 10 for i in range(1, 10))

    def __init__(
        self,
        model_path: str | Path = "models/timesfm-2.5",
        *,
        device: str = "cuda",
        context_length: int = 512,
        max_horizon: int = 256,
    ) -> None:
        self.model_path = Path(model_path)
        self.device = _device_name(device)
        self.context_length = context_length
        self.max_horizon = max_horizon
        self.name = "timesfm_2_5"
        self._model = None

    def _load(self):
        if self._model is not None:
            return self._model
        try:
            import timesfm
        except ImportError as exc:
            raise ModelDependencyError("Install inventory-fusion[timesfm]") from exc
        source = str(self.model_path) if self.model_path.exists() else self.MODEL_ID
        kwargs = {"torch_compile": False}
        if not self.model_path.exists():
            kwargs["revision"] = self.REVISION
        self._model = timesfm.TimesFM_2p5_200M_torch.from_pretrained(source, **kwargs)
        self._model.compile(
            timesfm.ForecastConfig(
                max_context=self.context_length,
                max_horizon=self.max_horizon,
                normalize_inputs=True,
                use_continuous_quantile_head=True,
                force_flip_invariance=True,
                infer_is_positive=True,
                fix_quantile_crossing=True,
            )
        )
        return self._model

    def predict(
        self,
        history: TimeSeries,
        horizon: int,
        *,
        future_dates: np.ndarray | None = None,
        future_covariates: Mapping[str, np.ndarray] | None = None,
        quantiles: tuple[float, ...] = DEFAULT_QUANTILES,
    ) -> Forecast:
        del future_dates, future_covariates
        if horizon > self.max_horizon:
            raise ValueError(f"TimesFM adapter supports at most {self.max_horizon} steps")
        _, native = self._load().forecast(
            horizon=horizon,
            inputs=[history.values[-self.context_length :].astype(np.float32)],
        )
        # TimesFM returns mean in column 0, followed by q0.1 ... q0.9.
        native_values = {
            q: native[0, :, index + 1] for index, q in enumerate(self.NATIVE_QUANTILES)
        }
        native_forecast = Forecast(self.name, history.sku, native_values)
        values = {q: native_forecast.quantile(q) for q in quantiles}
        return Forecast(
            model_name=self.name,
            sku=history.sku,
            values=values,
            metadata={"model_id": self.MODEL_ID, "revision": self.REVISION},
        )

    def close(self) -> None:
        self._model = None
        gc.collect()
        try:
            import torch

            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass
