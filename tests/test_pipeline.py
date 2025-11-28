import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.transcribe import transcribe_audio
from src.summarize import summarize_text

class TestPipeline(unittest.TestCase):

    @patch('src.transcribe.WhisperModel')
    def test_transcribe_audio(self, MockWhisperModel):
        # Setup mock
        mock_model = MockWhisperModel.return_value
        mock_segment = MagicMock()
        mock_segment.start = 0.0
        mock_segment.end = 1.0
        mock_segment.text = "Hello world"
        
        mock_info = MagicMock()
        mock_info.language = "ja"
        mock_info.language_probability = 0.99
        
        mock_model.transcribe.return_value = ([mock_segment], mock_info)
        
        # Run function
        transcript = transcribe_audio("dummy.m4a", device="cpu")
        
        # Verify
        self.assertIn("Hello world", transcript)
        MockWhisperModel.assert_called_once()
        mock_model.transcribe.assert_called_once()

    @patch('src.summarize.load')
    @patch('src.summarize.generate')
    def test_summarize_text(self, mock_generate, mock_load):
        # Setup mock
        mock_model = MagicMock()
        mock_tokenizer = MagicMock()
        mock_load.return_value = (mock_model, mock_tokenizer)
        mock_generate.return_value = "# Minutes\n\nSummary..."
        
        # Run function
        summary = summarize_text("This is a transcript.")
        
        # Verify
        self.assertIn("# Minutes", summary)
        mock_load.assert_called_once()
        mock_generate.assert_called_once()

if __name__ == '__main__':
    unittest.main()
