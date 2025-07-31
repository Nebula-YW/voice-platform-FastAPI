from lingua import Language, LanguageDetectorBuilder
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class LanguageDetectionService:
    """语言检测服务类，支持18种语言的高精度检测"""

    # 支持的语言映射 (lingua Language枚举 -> 语言信息)
    SUPPORTED_LANGUAGES = {
        Language.CHINESE: {"code": "zh", "name": "Chinese", "native_name": "中文"},
        Language.ENGLISH: {"code": "en", "name": "English", "native_name": "English"},
        Language.SPANISH: {"code": "es", "name": "Spanish", "native_name": "Español"},
        Language.PORTUGUESE: {
            "code": "pt",
            "name": "Portuguese",
            "native_name": "Português",
        },
        Language.ARABIC: {"code": "ar", "name": "Arabic", "native_name": "العربية"},
        Language.RUSSIAN: {"code": "ru", "name": "Russian", "native_name": "Русский"},
        Language.FRENCH: {"code": "fr", "name": "French", "native_name": "Français"},
        Language.GERMAN: {"code": "de", "name": "German", "native_name": "Deutsch"},
        Language.THAI: {"code": "th", "name": "Thai", "native_name": "ไทย"},
        Language.VIETNAMESE: {
            "code": "vi",
            "name": "Vietnamese",
            "native_name": "Tiếng Việt",
        },
        Language.INDONESIAN: {
            "code": "id",
            "name": "Indonesian",
            "native_name": "Bahasa Indonesia",
        },
        Language.MALAY: {"code": "ms", "name": "Malay", "native_name": "Bahasa Melayu"},
        Language.TURKISH: {"code": "tr", "name": "Turkish", "native_name": "Türkçe"},
        Language.ITALIAN: {"code": "it", "name": "Italian", "native_name": "Italiano"},
        Language.DUTCH: {"code": "nl", "name": "Dutch", "native_name": "Nederlands"},
        Language.POLISH: {"code": "pl", "name": "Polish", "native_name": "Polski"},
        Language.JAPANESE: {"code": "ja", "name": "Japanese", "native_name": "日本語"},
        Language.KOREAN: {"code": "ko", "name": "Korean", "native_name": "한국어"},
    }

    def __init__(self):
        """初始化语言检测器，仅加载支持的18种语言"""
        self._detector = None
        self._language_code_map = None
        self._initialize_detector()

    def _initialize_detector(self):
        """初始化lingua检测器，仅加载支持的语言以优化性能"""
        try:
            logger.info("Initializing language detector with 18 supported languages")

            # 构建仅包含支持语言的检测器
            languages = list(self.SUPPORTED_LANGUAGES.keys())
            self._detector = LanguageDetectorBuilder.from_languages(*languages).build()

            # 创建语言代码到Language枚举的反向映射
            self._language_code_map = {
                info["code"]: lang for lang, info in self.SUPPORTED_LANGUAGES.items()
            }

            logger.info(
                f"Language detector initialized successfully with {len(languages)} languages"
            )

        except Exception as e:
            logger.error(f"Failed to initialize language detector: {e}")
            raise

    def detect_language(self, text: str, with_confidence: bool = False) -> Dict:
        """
        检测单个文本的语言

        Args:
            text: 要检测的文本
            with_confidence: 是否返回置信度

        Returns:
            包含语言检测结果的字典
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        try:
            # 检测语言
            detected_language = self._detector.detect_language_of(text)

            if detected_language is None:
                # 如果无法检测，返回英语作为默认值
                detected_language = Language.ENGLISH
                confidence = 0.0
            else:
                # 获取置信度（如果需要）
                confidence = None
                if with_confidence:
                    confidence_values = (
                        self._detector.compute_language_confidence_values(text)
                    )
                    confidence = next(
                        (
                            cv.value
                            for cv in confidence_values
                            if cv.language == detected_language
                        ),
                        0.0,
                    )

            # 获取语言信息
            lang_info = self.SUPPORTED_LANGUAGES[detected_language]

            result = {
                "text": text,
                "language": lang_info["code"],
                "language_name": lang_info["name"],
            }

            if with_confidence:
                result["confidence"] = confidence

            return result

        except Exception as e:
            logger.error(
                f"Failed to detect language for text: {text[:50]}... Error: {e}"
            )
            raise

    def detect_languages_batch(
        self, texts: List[str], with_confidence: bool = False
    ) -> List[Dict]:
        """
        批量检测多个文本的语言

        Args:
            texts: 要检测的文本列表
            with_confidence: 是否返回置信度

        Returns:
            包含语言检测结果的字典列表
        """
        if not texts:
            raise ValueError("Texts list cannot be empty")

        results = []
        for text in texts:
            try:
                result = self.detect_language(text, with_confidence)
                results.append(result)
            except Exception as e:
                logger.error(
                    f"Failed to detect language for text in batch: {text[:50]}... Error: {e}"
                )
                # 为失败的检测添加默认结果
                default_result = {
                    "text": text,
                    "language": "en",
                    "language_name": "English",
                }
                if with_confidence:
                    default_result["confidence"] = 0.0
                results.append(default_result)

        return results

    def get_supported_languages(self) -> List[Dict]:
        """
        获取支持的语言列表

        Returns:
            支持的语言信息列表
        """
        return [
            {
                "code": info["code"],
                "name": info["name"],
                "native_name": info["native_name"],
            }
            for info in self.SUPPORTED_LANGUAGES.values()
        ]

    def is_language_supported(self, language_code: str) -> bool:
        """
        检查语言代码是否被支持

        Args:
            language_code: 语言代码 (如: 'zh', 'en')

        Returns:
            是否支持该语言
        """
        return language_code in self._language_code_map


# 全局单例实例
_language_service = None


def get_language_service() -> LanguageDetectionService:
    """获取语言检测服务单例实例"""
    global _language_service
    if _language_service is None:
        _language_service = LanguageDetectionService()
    return _language_service
