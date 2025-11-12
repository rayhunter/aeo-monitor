import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
import sys
import os

# Add parent directory to path to import app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import functions to test
from app import query_model, run_all_queries


class TestKeywordMatching:
    """Test keyword matching logic"""

    @pytest.mark.asyncio
    async def test_keyword_match_single_occurrence(self):
        """Test detecting a single keyword match"""
        mock_client = AsyncMock()
        mock_response = Mock()

        # Setup mock response
        mock_content = Mock()
        mock_content.text = "This response contains the word measurement in it."
        mock_content.annotations = []

        mock_output = Mock()
        mock_output.content = [mock_content]

        mock_response.output = [mock_output]
        mock_client.responses.create = AsyncMock(return_value=mock_response)

        # Test with keyword
        with patch('app.keywords', ['measurement']):
            result = await query_model(
                mock_client,
                "openai/gpt-4o",
                "Test prompt"
            )

        assert result['success'] is True
        assert len(result['keyword_matches']) == 1
        assert result['keyword_matches'][0]['keyword'] == 'measurement'
        assert result['keyword_matches'][0]['count'] == 1

    @pytest.mark.asyncio
    async def test_keyword_match_multiple_occurrences(self):
        """Test detecting multiple occurrences of the same keyword"""
        mock_client = AsyncMock()
        mock_response = Mock()

        mock_content = Mock()
        mock_content.text = "Impact analysis shows the impact of the impact measurement."
        mock_content.annotations = []

        mock_output = Mock()
        mock_output.content = [mock_content]

        mock_response.output = [mock_output]
        mock_client.responses.create = AsyncMock(return_value=mock_response)

        with patch('app.keywords', ['impact']):
            result = await query_model(
                mock_client,
                "openai/gpt-4o",
                "Test prompt"
            )

        assert result['success'] is True
        assert len(result['keyword_matches']) == 1
        assert result['keyword_matches'][0]['count'] == 3

    @pytest.mark.asyncio
    async def test_keyword_match_case_insensitive(self):
        """Test that keyword matching is case-insensitive"""
        mock_client = AsyncMock()
        mock_response = Mock()

        mock_content = Mock()
        mock_content.text = "STRATEGY and Strategy and strategy are all the same."
        mock_content.annotations = []

        mock_output = Mock()
        mock_output.content = [mock_content]

        mock_response.output = [mock_output]
        mock_client.responses.create = AsyncMock(return_value=mock_response)

        with patch('app.keywords', ['strategy']):
            result = await query_model(
                mock_client,
                "openai/gpt-4o",
                "Test prompt"
            )

        assert result['success'] is True
        assert len(result['keyword_matches']) == 1
        assert result['keyword_matches'][0]['count'] == 3

    @pytest.mark.asyncio
    async def test_no_keyword_match(self):
        """Test when no keywords are found"""
        mock_client = AsyncMock()
        mock_response = Mock()

        mock_content = Mock()
        mock_content.text = "This response has no matching keywords."
        mock_content.annotations = []

        mock_output = Mock()
        mock_output.content = [mock_content]

        mock_response.output = [mock_output]
        mock_client.responses.create = AsyncMock(return_value=mock_response)

        with patch('app.keywords', ['nonexistent']):
            result = await query_model(
                mock_client,
                "openai/gpt-4o",
                "Test prompt"
            )

        assert result['success'] is True
        assert len(result['keyword_matches']) == 0

    @pytest.mark.asyncio
    async def test_multiple_different_keywords(self):
        """Test detecting multiple different keywords"""
        mock_client = AsyncMock()
        mock_response = Mock()

        mock_content = Mock()
        mock_content.text = "Analysis shows measurement of strategy impact."
        mock_content.annotations = []

        mock_output = Mock()
        mock_output.content = [mock_content]

        mock_response.output = [mock_output]
        mock_client.responses.create = AsyncMock(return_value=mock_response)

        with patch('app.keywords', ['analysis', 'measurement', 'strategy', 'impact']):
            result = await query_model(
                mock_client,
                "openai/gpt-4o",
                "Test prompt"
            )

        assert result['success'] is True
        assert len(result['keyword_matches']) == 4


class TestDomainMatching:
    """Test domain citation matching logic"""

    @pytest.mark.asyncio
    async def test_domain_match_in_citation(self):
        """Test detecting domain in citation URL"""
        mock_client = AsyncMock()
        mock_response = Mock()

        mock_content = Mock()
        mock_content.text = "Some response text."

        # Mock annotation with URL
        mock_annotation = Mock()
        mock_annotation.url = "https://thecompany.ai/article"
        mock_content.annotations = [mock_annotation]

        mock_output = Mock()
        mock_output.content = [mock_content]

        mock_response.output = [mock_output]
        mock_client.responses.create = AsyncMock(return_value=mock_response)

        with patch('app.keywords', []):
            with patch('app.domains', ['thecompany.ai']):
                result = await query_model(
                    mock_client,
                    "openai/gpt-4o",
                    "Test prompt"
                )

        assert result['success'] is True
        assert len(result['domain_matches']) == 1
        assert result['domain_matches'][0]['domain'] == 'thecompany.ai'
        assert 'thecompany.ai' in result['domain_matches'][0]['url']

    @pytest.mark.asyncio
    async def test_multiple_domain_matches(self):
        """Test detecting multiple domain citations"""
        mock_client = AsyncMock()
        mock_response = Mock()

        mock_content = Mock()
        mock_content.text = "Some response text."

        # Mock multiple annotations
        mock_annotation1 = Mock()
        mock_annotation1.url = "https://thecompany.ai/article1"
        mock_annotation2 = Mock()
        mock_annotation2.url = "https://thecompany.com/article2"
        mock_annotation3 = Mock()
        mock_annotation3.url = "https://other.com/article"

        mock_content.annotations = [mock_annotation1, mock_annotation2, mock_annotation3]

        mock_output = Mock()
        mock_output.content = [mock_content]

        mock_response.output = [mock_output]
        mock_client.responses.create = AsyncMock(return_value=mock_response)

        with patch('app.keywords', []):
            with patch('app.domains', ['thecompany.ai', 'thecompany.com']):
                result = await query_model(
                    mock_client,
                    "openai/gpt-4o",
                    "Test prompt"
                )

        assert result['success'] is True
        assert len(result['domain_matches']) == 2
        assert result['total_citations'] == 3

    @pytest.mark.asyncio
    async def test_domain_match_case_insensitive(self):
        """Test that domain matching is case-insensitive"""
        mock_client = AsyncMock()
        mock_response = Mock()

        mock_content = Mock()
        mock_content.text = "Some response text."

        mock_annotation = Mock()
        mock_annotation.url = "https://THECOMPANY.AI/Article"
        mock_content.annotations = [mock_annotation]

        mock_output = Mock()
        mock_output.content = [mock_content]

        mock_response.output = [mock_output]
        mock_client.responses.create = AsyncMock(return_value=mock_response)

        with patch('app.keywords', []):
            with patch('app.domains', ['thecompany.ai']):
                result = await query_model(
                    mock_client,
                    "openai/gpt-4o",
                    "Test prompt"
                )

        assert result['success'] is True
        assert len(result['domain_matches']) == 1

    @pytest.mark.asyncio
    async def test_no_domain_match(self):
        """Test when no domains are found in citations"""
        mock_client = AsyncMock()
        mock_response = Mock()

        mock_content = Mock()
        mock_content.text = "Some response text."

        mock_annotation = Mock()
        mock_annotation.url = "https://other.com/article"
        mock_content.annotations = [mock_annotation]

        mock_output = Mock()
        mock_output.content = [mock_content]

        mock_response.output = [mock_output]
        mock_client.responses.create = AsyncMock(return_value=mock_response)

        with patch('app.keywords', []):
            with patch('app.domains', ['thecompany.ai']):
                result = await query_model(
                    mock_client,
                    "openai/gpt-4o",
                    "Test prompt"
                )

        assert result['success'] is True
        assert len(result['domain_matches']) == 0
        assert result['total_citations'] == 1


class TestQueryModel:
    """Test the query_model async function"""

    @pytest.mark.asyncio
    async def test_successful_query(self):
        """Test a successful query returns expected structure"""
        mock_client = AsyncMock()
        mock_response = Mock()

        mock_content = Mock()
        mock_content.text = "Test response content"
        mock_content.annotations = []

        mock_output = Mock()
        mock_output.content = [mock_content]

        mock_response.output = [mock_output]
        mock_client.responses.create = AsyncMock(return_value=mock_response)

        with patch('app.keywords', []):
            with patch('app.domains', []):
                result = await query_model(
                    mock_client,
                    "openai/gpt-4o",
                    "Test prompt"
                )

        assert result['success'] is True
        assert result['model'] == "openai/gpt-4o"
        assert result['prompt'] == "Test prompt"
        assert 'content' in result
        assert 'keyword_matches' in result
        assert 'domain_matches' in result
        assert 'citation_urls' in result
        assert 'total_citations' in result
        assert 'timestamp' in result

    @pytest.mark.asyncio
    async def test_query_with_error(self):
        """Test that errors are handled gracefully"""
        mock_client = AsyncMock()
        mock_client.responses.create = AsyncMock(side_effect=Exception("API Error"))

        with patch('app.keywords', []):
            with patch('app.domains', []):
                result = await query_model(
                    mock_client,
                    "openai/gpt-4o",
                    "Test prompt"
                )

        assert result['success'] is False
        assert 'error' in result
        assert result['error'] == "API Error"
        assert result['model'] == "openai/gpt-4o"
        assert result['prompt'] == "Test prompt"

    @pytest.mark.asyncio
    async def test_query_calls_api_with_correct_params(self):
        """Test that the API is called with correct parameters"""
        mock_client = AsyncMock()
        mock_response = Mock()

        mock_content = Mock()
        mock_content.text = "Test response"
        mock_content.annotations = []

        mock_output = Mock()
        mock_output.content = [mock_content]

        mock_response.output = [mock_output]
        mock_client.responses.create = AsyncMock(return_value=mock_response)

        with patch('app.keywords', []):
            with patch('app.domains', []):
                await query_model(
                    mock_client,
                    "openai/gpt-4o",
                    "Test prompt"
                )

        # Verify the API was called with correct parameters
        mock_client.responses.create.assert_called_once()
        call_args = mock_client.responses.create.call_args

        assert call_args[1]['model'] == "openai/gpt-4o:online"
        assert call_args[1]['stream'] is False
        assert len(call_args[1]['input']) == 1
        assert call_args[1]['input'][0]['role'] == "user"
        assert call_args[1]['input'][0]['content'] == "Test prompt"

    @pytest.mark.asyncio
    async def test_posthog_event_sent_on_success(self):
        """Test that PostHog event is sent on successful query"""
        mock_client = AsyncMock()
        mock_response = Mock()

        mock_content = Mock()
        mock_content.text = "Test response with measurement"
        mock_content.annotations = []

        mock_output = Mock()
        mock_output.content = [mock_content]

        mock_response.output = [mock_output]
        mock_client.responses.create = AsyncMock(return_value=mock_response)

        mock_posthog = Mock()

        with patch('app.keywords', ['measurement']):
            with patch('app.domains', []):
                with patch('app.enable_posthog', True):
                    await query_model(
                        mock_client,
                        "openai/gpt-4o",
                        "Test prompt",
                        mock_posthog
                    )

        # Verify PostHog capture was called
        mock_posthog.capture.assert_called_once()
        call_args = mock_posthog.capture.call_args[1]

        assert call_args['distinct_id'] == "aeo_monitor_openai/gpt-4o"
        assert call_args['event'] == "aeo_query_completed"
        assert 'model' in call_args['properties']
        assert 'prompt' in call_args['properties']


class TestRunAllQueries:
    """Test the run_all_queries batch function"""

    @pytest.mark.asyncio
    async def test_run_multiple_queries(self):
        """Test running multiple models and prompts"""
        mock_client = AsyncMock()
        mock_response = Mock()

        mock_content = Mock()
        mock_content.text = "Test response"
        mock_content.annotations = []

        mock_output = Mock()
        mock_output.content = [mock_content]

        mock_response.output = [mock_output]

        # Make the mock return the response each time
        async def mock_create(*args, **kwargs):
            return mock_response

        with patch('app.AsyncOpenAI') as mock_async_client_class:
            mock_instance = AsyncMock()
            mock_instance.responses.create = AsyncMock(side_effect=mock_create)
            mock_async_client_class.return_value = mock_instance

            with patch('app.keywords', []):
                with patch('app.domains', []):
                    results = await run_all_queries(
                        "test-api-key",
                        ["openai/gpt-4o", "perplexity/sonar-pro"],
                        ["Prompt 1", "Prompt 2"]
                    )

        # Should have 2 models * 2 prompts = 4 results
        assert len(results) == 4
        assert all(r['success'] for r in results)

    @pytest.mark.asyncio
    async def test_progress_callback_called(self):
        """Test that progress callback is called correctly"""
        mock_client = AsyncMock()
        mock_response = Mock()

        mock_content = Mock()
        mock_content.text = "Test response"
        mock_content.annotations = []

        mock_output = Mock()
        mock_output.content = [mock_content]

        mock_response.output = [mock_output]

        callback_calls = []

        def progress_callback(completed, total, result):
            callback_calls.append((completed, total, result))

        async def mock_create(*args, **kwargs):
            return mock_response

        with patch('app.AsyncOpenAI') as mock_async_client_class:
            mock_instance = AsyncMock()
            mock_instance.responses.create = AsyncMock(side_effect=mock_create)
            mock_async_client_class.return_value = mock_instance

            with patch('app.keywords', []):
                with patch('app.domains', []):
                    await run_all_queries(
                        "test-api-key",
                        ["openai/gpt-4o"],
                        ["Prompt 1", "Prompt 2"],
                        progress_callback=progress_callback
                    )

        # Should have been called twice (once for each prompt)
        assert len(callback_calls) == 2
        assert callback_calls[0][0] == 1  # First completion
        assert callback_calls[1][0] == 2  # Second completion
        assert callback_calls[0][1] == 2  # Total tasks
        assert callback_calls[1][1] == 2  # Total tasks


class TestIntegration:
    """Integration tests combining multiple components"""

    @pytest.mark.asyncio
    async def test_full_query_with_matches(self):
        """Test complete query flow with keyword and domain matches"""
        mock_client = AsyncMock()
        mock_response = Mock()

        mock_content = Mock()
        mock_content.text = "This article discusses measurement and analysis strategies."

        # Mock citations
        mock_annotation1 = Mock()
        mock_annotation1.url = "https://thecompany.ai/article"
        mock_annotation2 = Mock()
        mock_annotation2.url = "https://other.com/article"

        mock_content.annotations = [mock_annotation1, mock_annotation2]

        mock_output = Mock()
        mock_output.content = [mock_content]

        mock_response.output = [mock_output]
        mock_client.responses.create = AsyncMock(return_value=mock_response)

        with patch('app.keywords', ['measurement', 'analysis', 'strategy']):
            with patch('app.domains', ['thecompany.ai']):
                result = await query_model(
                    mock_client,
                    "openai/gpt-4o",
                    "What are the best tools?"
                )

        assert result['success'] is True
        assert len(result['keyword_matches']) == 3
        assert len(result['domain_matches']) == 1
        assert result['total_citations'] == 2

        # Verify specific matches
        keyword_names = [m['keyword'] for m in result['keyword_matches']]
        assert 'measurement' in keyword_names
        assert 'analysis' in keyword_names
        assert 'strategy' in keyword_names

        assert result['domain_matches'][0]['domain'] == 'thecompany.ai'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
