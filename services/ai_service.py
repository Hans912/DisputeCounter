import os
from dotenv import load_dotenv
import pandas as pd
import google.generativeai as genai
import logging

load_dotenv()

# Configure a dedicated logger for AI
logger = logging.getLogger("ai_service")
if not logger.handlers:
    logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))
    fh = logging.FileHandler("ai_service.log", encoding="utf-8")
    ch = logging.StreamHandler()
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    fh.setFormatter(fmt)
    ch.setFormatter(fmt)
    logger.addHandler(fh)
    logger.addHandler(ch)

class GeminiAIService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set in environment.")
        genai.configure(api_key=api_key)
        # You can change the model if desired
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        logger.info("GeminiAIService initialized with model gemini-2.5-flash")

    def summarize_messages(self, messages_df: pd.DataFrame) -> str:
        if messages_df is None or messages_df.empty:
            logger.warning("summarize_messages called with empty messages_df")
            return "No customer messages available for summary."

        # Flatten messages into compact text
        lines = []
        for _, row in messages_df.iterrows():
            date = str(row.get("Date", "") or "")
            status = str(row.get("Status", "") or "")
            body = str(row.get("Message", "") or "")
            lines.append(f"{date} | {status} | {body[:500]}")

        total_lines = len(lines)
        content = "\n".join(lines[:200])  # cap size for prompt safety
        logger.info(f"Preparing summary prompt: total_lines={total_lines}, used_lines={min(200, total_lines)}, prompt_chars={len(content)}")

        prompt = f"""
You assist with payment dispute evidence. Summarize the following SMS messages clearly and neutrally.
- 8–12 sentences, concise and factual
- Note key customer intents, confirmations, refund requests, and outcomes
- Include timeline anchors (dates) when relevant
- Avoid speculation or sensitive data; only use what is present

Messages:
{content}
"""

        try:
            resp = self.model.generate_content(prompt)
            logger.debug(
                f"Gemini response type: {type(resp)}; "
                f"candidates={len(getattr(resp, 'candidates', []) or [])}"
            )
            text = self._extract_text(resp)
            logger.info(f"Summary generated: length={len(text)} chars")
            return text.strip() if text.strip() else "Summary could not be generated."
        except Exception:
            logger.exception("Error during Gemini summary generation")
            return "Summary could not be generated. Check ai_service.log for details."

    def _extract_text(self, resp) -> str:
        """
        Extract text from candidates/parts without using resp.text,
        which can raise 'Part is not iterable' in some SDK versions.
        """
        collected = []
        try:
            candidates = getattr(resp, "candidates", []) or []
            logger.debug(f"Response candidates: {len(candidates)}")
            for i, cand in enumerate(candidates):
                content = getattr(cand, "content", None)
                parts = getattr(content, "parts", []) if content else []
                logger.debug(f"Candidate {i} parts: {len(parts)}")
                for part in parts:
                    txt = getattr(part, "text", None)
                    if isinstance(txt, str) and txt.strip():
                        collected.append(txt.strip())
            if collected:
                return "\n".join(collected)
        except Exception:
            logger.exception("Failed to extract text from candidates/parts")
        logger.warning("No text found in Gemini response")
        return ""