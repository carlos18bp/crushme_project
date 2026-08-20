"""Resource-bounded CTranslate2 engine for the local translation daemon."""

from __future__ import annotations

import gc
from pathlib import Path

from .translation_manifest import MODEL_SPECS, validate_model_bundle


class CpuTranslationEngine:
    """Translate ES/EN offline while keeping at most one model resident."""

    def __init__(self, model_dir: Path):
        self.model_dir = model_dir.expanduser().resolve()
        validate_model_bundle(self.model_dir)
        self._active_pair: tuple[str, str] | None = None
        self._translator = None
        self._source_tokenizer = None
        self._target_tokenizer = None
        self._segmenter = None

    @property
    def active_pair(self) -> tuple[str, str] | None:
        return self._active_pair

    def _unload(self) -> None:
        if self._translator is not None:
            unload_model = getattr(self._translator, "unload_model", None)
            if unload_model is not None:
                unload_model()
        self._translator = None
        self._source_tokenizer = None
        self._target_tokenizer = None
        self._segmenter = None
        self._active_pair = None
        gc.collect()

    def _load(self, pair: tuple[str, str]) -> None:
        if self._active_pair == pair:
            return
        if pair not in MODEL_SPECS:
            raise ValueError(f"Unsupported language pair: {pair[0]}->{pair[1]}")

        import ctranslate2
        import pysbd
        import sentencepiece as sentencepiece

        self._unload()
        spec = MODEL_SPECS[pair]
        model_path = self.model_dir / spec.directory
        supported_types = ctranslate2.get_supported_compute_types("cpu")
        if "int8" not in supported_types:
            raise RuntimeError("CTranslate2 runtime does not support int8 on this CPU")

        self._translator = ctranslate2.Translator(
            str(model_path),
            device="cpu",
            compute_type="int8",
            inter_threads=1,
            intra_threads=1,
        )
        self._source_tokenizer = sentencepiece.SentencePieceProcessor(
            model_file=str(model_path / "source.spm")
        )
        self._target_tokenizer = sentencepiece.SentencePieceProcessor(
            model_file=str(model_path / "target.spm")
        )
        self._segmenter = pysbd.Segmenter(language=pair[0], clean=False)
        self._active_pair = pair

    def _translate_paragraph(self, paragraph: str) -> str:
        segments = [segment.strip() for segment in self._segmenter.segment(paragraph)]
        segments = [segment for segment in segments if segment]
        if not segments:
            return paragraph

        tokenized = [
            self._source_tokenizer.encode(segment, out_type=str) + ["</s>"]
            for segment in segments
        ]
        max_source_tokens = max(len(tokens) for tokens in tokenized)
        max_decoding_length = min(512, max(64, max_source_tokens * 3))
        results = self._translator.translate_batch(
            tokenized,
            beam_size=4,
            num_hypotheses=1,
            max_batch_size=8,
            batch_type="tokens",
            max_decoding_length=max_decoding_length,
            length_penalty=0.2,
            return_scores=True,
        )
        translated = [
            self._target_tokenizer.decode(result.hypotheses[0]).strip()
            for result in results
        ]
        return " ".join(part for part in translated if part)

    def translate(self, text: str, source_language: str, target_language: str) -> str:
        pair = source_language, target_language
        if source_language == target_language:
            return text
        self._load(pair)
        return "\n".join(
            self._translate_paragraph(paragraph) if paragraph.strip() else paragraph
            for paragraph in text.split("\n")
        )
