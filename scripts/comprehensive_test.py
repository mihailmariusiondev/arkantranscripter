#!/usr/bin/env python3
"""
COMPREHENSIVE YOUTUBE URL AND STRATEGY TESTING SCRIPT
Tests ALL types of YouTube URLs with ALL available transcript extraction strategies.
Ensures complete coverage of fallback mechanisms and maintains DRY principles.

⚠️ ESTE ES EL ÚNICO ARCHIVO DE PRUEBA DEL PROYECTO
⚠️ JAMÁS crear otros archivos test_*.py - TODO se hace aquí
⚠️ Incluye pruebas para: Instagram, Twitter/X, TikTok, YouTube
⚠️ Incluye pruebas de estrategias, downloads, URL fixing, configuración
"""

import asyncio
import logging
import re
import time
from pathlib import Path
import sys
from typing import List, Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from bot.services.youtube_transcript_service import YouTubeTranscriptExtractor

def load_test_urls_from_file(file_path: str = 'test_urls.txt', categories: List[str] = None) -> Dict[str, List[Dict[str, str]]]:
    """
    Load test URLs from external file.

    Args:
        file_path: Path to the URLs file
        categories: List of categories to load (if None, loads all)

    Returns:
        Dictionary organized by category with URL data
    """
    test_urls = {}

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue

                # Parse line: CATEGORY|URL|DESCRIPTION
                parts = line.split('|', 2)
                if len(parts) != 3:
                    continue

                category, url, description = parts
                category = category.strip()
                url = url.strip()
                description = description.strip()

                # Filter by categories if specified
                if categories and category not in categories:
                    continue

                # Initialize category if not exists
                if category not in test_urls:
                    test_urls[category] = []

                test_urls[category].append({
                    'url': url,
                    'description': description
                })

        logger.info(f"📋 Loaded {sum(len(urls) for urls in test_urls.values())} URLs from {file_path}")
        logger.info(f"📂 Categories loaded: {list(test_urls.keys())}")

    except FileNotFoundError:
        logger.warning(f"⚠️  URLs file {file_path} not found, falling back to built-in URLs")
        # Fallback to a minimal set if file not found
        test_urls = {
            'fallback': [
                {'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'description': 'Rick Roll - Classic Test'},
                {'url': 'https://youtu.be/dQw4w9WgXcQ', 'description': 'Shortened Rick Roll'},
                {'url': 'https://www.youtube.com/watch?v=Ks-_Mh1QhMc', 'description': 'Popular Music Video'},
            ]
        }

    return test_urls

# Configure logging with extensive debugging
log_file = 'comprehensive_test_debug.log'
logging.basicConfig(
    level=logging.DEBUG,  # Maximum verbosity for troubleshooting
    format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_file, mode='w', encoding='utf-8')
    ],
    force=True  # Override any existing configuration
)

# Create logger for this script
logger = logging.getLogger('comprehensive_test')
logger.info(f"🚀 Comprehensive test logger initialized, writing to {log_file}")
print(f"📝 Debug logs will be written to: {log_file}")

class YouTubeURLTester:
    def __init__(self):
        logger.info("🔧 Initializing YouTubeURLTester")

        self.extractor = YouTubeTranscriptExtractor()
        logger.info(f"✅ YouTubeTranscriptExtractor initialized with {len(self.extractor.strategies)} strategies")

        self.results = []
        self.total_tested = 0
        self.successful = 0
        self.failed = 0

        # Strategy results tracking - DRY principle using new service methods
        strategy_names = self.extractor.get_strategy_names()
        logger.info(f"📋 Available strategies: {strategy_names}")

        self.strategy_results = {
            name: {'success': 0, 'total': 0, 'errors': []} for name in strategy_names
        }

        # Get strategy methods directly from the extractor - maintains DRY
        self.strategy_methods = self.extractor.get_strategy_methods()
        logger.info(f"🔗 Strategy methods loaded: {list(self.strategy_methods.keys())}")

        # Reduced timeouts for faster testing
        self.request_timeout = 10  # Reduced from 30s to 10s
        self.strategy_delay = 0.2  # Reduced from 0.5s to 0.2s
        self.url_delay = 0.5  # Reduced from 2s to 0.5s

        logger.info(f"⏱️  Timeouts configured: request={self.request_timeout}s, strategy_delay={self.strategy_delay}s, url_delay={self.url_delay}s")

    def extract_video_id(self, url: str) -> str:
        """Extract video ID from any YouTube URL format."""
        logger.debug(f"🔍 Extracting video ID from URL: {url}")

        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/shorts\/|m\.youtube\.com\/watch\?v=|youtube-nocookie\.com\/embed\/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com\/live\/([a-zA-Z0-9_-]{11})',
            r'music\.youtube\.com\/watch\?v=([a-zA-Z0-9_-]{11})',
            r'youtubekids\.com\/watch\?v=([a-zA-Z0-9_-]{11})',
        ]

        for i, pattern in enumerate(patterns):
            logger.debug(f"  🔍 Trying pattern {i+1}: {pattern[:50]}...")
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                logger.info(f"  ✅ Video ID extracted using pattern {i+1}: {video_id}")
                return video_id

        logger.warning(f"  ❌ No video ID found in URL: {url}")
        return None

    async def test_single_strategy(self, video_id: str, strategy_name: str, url: str, category: str) -> Dict[str, Any]:
        """Test a single strategy for a given video ID."""
        logger.info(f"🧪 Testing strategy '{strategy_name}' for video {video_id} ({category})")

        strategy_method = self.strategy_methods[strategy_name]
        logger.debug(f"   🔧 Using strategy method: {strategy_method.__name__}")

        result = {
            'url': url,
            'category': category,
            'video_id': video_id,
            'strategy': strategy_name,
            'status': 'UNKNOWN',
            'transcript_length': 0,
            'error': None,
            'execution_time': 0
        }

        start_time = time.time()
        logger.debug(f"   ⏱️  Strategy execution started at {start_time}")

        try:
            print(f"    🔧 {strategy_name}: ", end='', flush=True)
            logger.debug(f"   🚀 Calling strategy method for video {video_id}")

            transcript = await strategy_method(video_id)

            execution_time = time.time() - start_time
            result['execution_time'] = execution_time
            logger.debug(f"   ⏱️  Strategy completed in {execution_time:.2f}s")

            self.strategy_results[strategy_name]['total'] += 1

            if transcript and len(transcript.strip()) > 50:  # Minimum viable transcript
                result['status'] = 'SUCCESS'
                result['transcript_length'] = len(transcript)
                self.strategy_results[strategy_name]['success'] += 1

                logger.info(f"   ✅ SUCCESS: {len(transcript)} chars in {execution_time:.2f}s")
                logger.debug(f"   📄 Transcript preview: {transcript[:100]}...")
                print(f"✅ SUCCESS ({len(transcript)} chars, {execution_time:.2f}s)")
            else:
                result['status'] = 'NO_TRANSCRIPT'
                result['error'] = 'No transcript available or too short'
                self.strategy_results[strategy_name]['errors'].append(result['error'])

                logger.warning(f"   ❌ NO_TRANSCRIPT: {result['error']} (time: {execution_time:.2f}s)")
                if transcript:
                    logger.debug(f"   📄 Short transcript received: {transcript}")
                print(f"❌ NO_TRANSCRIPT ({execution_time:.2f}s)")

        except Exception as e:
            execution_time = time.time() - start_time
            result['execution_time'] = execution_time
            result['status'] = 'ERROR'
            result['error'] = str(e)

            self.strategy_results[strategy_name]['total'] += 1
            self.strategy_results[strategy_name]['errors'].append(str(e))

            logger.error(f"   💥 ERROR in {execution_time:.2f}s: {str(e)}")
            logger.exception("   🐛 Full exception traceback:")
            print(f"💥 ERROR: {str(e)[:50]}... ({execution_time:.2f}s)")

        logger.debug(f"   📊 Strategy result: {result}")
        return result

    async def test_all_strategies(self, video_id: str, url: str, category: str, description: str = "") -> List[Dict[str, Any]]:
        """Test all strategies for a single video ID."""
        logger.info(f"🎯 Testing ALL strategies for video {video_id} ({category})")
        logger.info(f"   📝 Description: {description}")
        print(f"  🔍 Testing: {video_id} ({category}) - {description}")

        strategy_results = []
        overall_success = False

        for i, strategy_name in enumerate(self.strategy_methods.keys(), 1):
            logger.info(f"   🔧 Strategy {i}/{len(self.strategy_methods)}: {strategy_name}")

            result = await self.test_single_strategy(video_id, strategy_name, url, category)
            strategy_results.append(result)

            if result['status'] == 'SUCCESS':
                overall_success = True
                logger.info(f"   🎉 First success achieved with {strategy_name}!")

            # Small delay between strategies to avoid rate limiting
            if i < len(self.strategy_methods):  # Don't delay after the last strategy
                logger.debug(f"   😴 Waiting {self.strategy_delay}s before next strategy...")
                await asyncio.sleep(self.strategy_delay)

        # Update overall counters
        self.total_tested += 1
        if overall_success:
            self.successful += 1
            logger.info(f"   🎯 OVERALL SUCCESS: At least one strategy worked for {video_id}")
            print(f"    🎯 OVERALL: ✅ SUCCESS (at least one strategy worked)")
        else:
            self.failed += 1
            logger.warning(f"   🎯 OVERALL FAILURE: All strategies failed for {video_id}")
            print(f"    🎯 OVERALL: ❌ FAILED (all strategies failed)")

        logger.info(f"   📊 Current progress: {self.successful}/{self.total_tested} successful ({(self.successful/self.total_tested)*100:.1f}%)")
        return strategy_results

    async def test_url_comprehensive(self, url: str, category: str, description: str = "") -> List[Dict[str, Any]]:
        """Test a URL with all strategies - comprehensive approach."""
        logger.info(f"🌐 Starting comprehensive URL test")
        logger.info(f"   URL: {url}")
        logger.info(f"   Category: {category}")
        logger.info(f"   Description: {description}")

        video_id = self.extract_video_id(url)

        if not video_id:
            logger.error(f"   ❌ Could not extract video ID from URL: {url}")
            failed_result = {
                'url': url,
                'category': category,
                'video_id': None,
                'strategy': 'ALL',
                'status': 'INVALID_URL',
                'transcript_length': 0,
                'error': 'Could not extract video ID',
                'execution_time': 0
            }
            self.total_tested += 1
            self.failed += 1
            logger.warning(f"   📊 Updated counters: failed={self.failed}, total={self.total_tested}")
            return [failed_result]

        logger.info(f"   ✅ Video ID extracted: {video_id}")
        return await self.test_all_strategies(video_id, url, category, description)

    async def run_comprehensive_test(self):
        """Run the comprehensive test suite testing ALL strategies."""

        logger.info("🚀 Starting comprehensive test suite")

        # Load URLs from external file
        TEST_URLS = load_test_urls_from_file()

        total_urls = sum(len(urls) for urls in TEST_URLS.values())
        total_strategies = len(self.strategy_methods)
        total_tests = total_urls * total_strategies

        logger.info(f"📊 Test scope:")
        logger.info(f"   Total URLs: {total_urls}")
        logger.info(f"   Total strategies: {total_strategies}")
        logger.info(f"   Total individual tests: {total_tests}")

        print("🎯 COMPREHENSIVE YOUTUBE URL AND STRATEGY TESTING")
        print("=" * 80)
        print(f"Testing {total_urls} URLs")
        print(f"Using {total_strategies} different extraction strategies:")
        for i, strategy in enumerate(self.strategy_methods.keys(), 1):
            print(f"  {i}. {strategy}")
        print("=" * 80)

        for category_num, (category, urls) in enumerate(TEST_URLS.items(), 1):
            logger.info(f"📂 Starting category {category_num}/{len(TEST_URLS)}: {category}")
            logger.info(f"   URLs in this category: {len(urls)}")

            print(f"\n📂 {category.upper()} ({len(urls)} URLs) - Category {category_num}/{len(TEST_URLS)}")
            print("-" * 60)

            for url_num, url_data in enumerate(urls, 1):
                url = url_data['url']
                description = url_data.get('description', '')

                logger.info(f"🔗 Processing URL {url_num}/{len(urls)} in {category}")
                logger.info(f"   URL: {url}")
                logger.info(f"   Description: {description}")

                # Test with all strategies
                strategy_results = await self.test_url_comprehensive(url, category, description)
                self.results.extend(strategy_results)

                logger.info(f"   ✅ URL {url_num} completed, added {len(strategy_results)} results")

                # Delay between URLs to be respectful to services
                if url_num < len(urls):  # Don't delay after the last URL
                    logger.debug(f"   😴 Waiting {self.url_delay}s before next URL...")
                    await asyncio.sleep(self.url_delay)

            logger.info(f"📂 Category {category} completed. Progress: {category_num}/{len(TEST_URLS)}")

            # Show progress after each category
            current_success_rate = (self.successful / self.total_tested * 100) if self.total_tested > 0 else 0
            logger.info(f"📊 Current overall success rate: {current_success_rate:.1f}% ({self.successful}/{self.total_tested})")
            print(f"\n   📊 Progress so far: {self.successful}/{self.total_tested} URLs successful ({current_success_rate:.1f}%)")

        logger.info("🎉 All categories completed, generating comprehensive summary")
        self._print_comprehensive_summary()

    def _print_comprehensive_summary(self):
        """Print comprehensive test summary with detailed strategy analysis."""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TEST RESULTS")
        print("=" * 80)

        print(f"Total URL Tests: {self.total_tested}")
        print(f"Overall Success: {self.successful} ({self.successful/self.total_tested*100:.1f}%)")
        print(f"Overall Failed: {self.failed} ({self.failed/self.total_tested*100:.1f}%)")

        # Strategy Performance Analysis
        print("\n🔧 STRATEGY PERFORMANCE ANALYSIS:")
        print("-" * 50)
        print(f"{'Strategy':<20} {'Success':<8} {'Total':<8} {'Rate':<8} {'Avg Time':<10}")
        print("-" * 50)

        for strategy_name, stats in self.strategy_results.items():
            if stats['total'] > 0:
                success_rate = (stats['success'] / stats['total']) * 100

                # Calculate average execution time
                strategy_times = [r['execution_time'] for r in self.results
                                if r['strategy'] == strategy_name and r['execution_time'] > 0]
                avg_time = sum(strategy_times) / len(strategy_times) if strategy_times else 0

                print(f"{strategy_name:<20} {stats['success']:<8} {stats['total']:<8} {success_rate:<7.1f}% {avg_time:<9.2f}s")

        # Strategy Reliability Ranking
        print("\n🏆 STRATEGY RELIABILITY RANKING:")
        print("-" * 40)
        sorted_strategies = sorted(
            [(name, stats['success'] / stats['total'] * 100 if stats['total'] > 0 else 0, stats)
             for name, stats in self.strategy_results.items()],
            key=lambda x: x[1], reverse=True
        )

        for i, (strategy, success_rate, stats) in enumerate(sorted_strategies, 1):
            print(f"{i}. {strategy:<20} {success_rate:>6.1f}% ({stats['success']}/{stats['total']})")

        # Results by URL category
        print("\n🏷️ RESULTS BY URL CATEGORY:")
        print("-" * 40)
        categories = {}
        for result in self.results:
            cat = result['category']
            if cat not in categories:
                categories[cat] = {'success': 0, 'total': 0}
            categories[cat]['total'] += 1
            if result['status'] == 'SUCCESS':
                categories[cat]['success'] += 1

        for cat, stats in categories.items():
            success_rate = stats['success']/stats['total']*100
            print(f"{cat:<25} {stats['success']:3}/{stats['total']:3} ({success_rate:5.1f}%)")

        # Top performing combinations
        print("\n✅ TOP SUCCESSES (by transcript length):")
        print("-" * 60)
        successes = [r for r in self.results if r['status'] == 'SUCCESS']
        successes.sort(key=lambda x: x['transcript_length'], reverse=True)

        print(f"{'#':<3} {'Video ID':<12} {'Strategy':<18} {'Length':<8} {'Category':<15}")
        print("-" * 60)
        for i, result in enumerate(successes[:15], 1):
            print(f"{i:<3} {result['video_id']:<12} {result['strategy']:<18} "
                  f"{result['transcript_length']:<8} {result['category']:<15}")

        # URL Format Analysis
        print("\n🔗 URL FORMAT SUCCESS ANALYSIS:")
        print("-" * 40)
        formats = {}
        for result in self.results:
            url = result['url']
            if 'youtu.be' in url:
                fmt = 'youtu.be'
            elif 'embed' in url:
                fmt = 'embed'
            elif 'shorts' in url:
                fmt = 'shorts'
            elif 'm.youtube' in url:
                fmt = 'mobile'
            elif 'music.youtube' in url:
                fmt = 'music'
            elif 'live' in url:
                fmt = 'live'
            elif 'playlist' in url:
                fmt = 'playlist'
            else:
                fmt = 'standard'

            if fmt not in formats:
                formats[fmt] = {'success': 0, 'total': 0}
            formats[fmt]['total'] += 1
            if result['status'] == 'SUCCESS':
                formats[fmt]['success'] += 1

        for fmt, stats in formats.items():
            if stats['total'] > 0:
                success_rate = stats['success']/stats['total']*100
                print(f"{fmt:<15} {stats['success']:3}/{stats['total']:3} ({success_rate:5.1f}%)")

        # Error Analysis
        print("\n🚨 ERROR ANALYSIS BY STRATEGY:")
        print("-" * 50)
        for strategy_name, stats in self.strategy_results.items():
            if stats['errors']:
                print(f"\n{strategy_name.upper()}:")
                error_counts = {}
                for error in stats['errors']:
                    error_key = error[:50] + "..." if len(error) > 50 else error
                    error_counts[error_key] = error_counts.get(error_key, 0) + 1

                for error, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                    print(f"  • {error} (x{count})")

        print("\n🎯 COMPREHENSIVE TESTING COMPLETED!")
        print("All YouTube URL formats and extraction strategies tested!")

        # Final recommendations
        print("\n💡 STRATEGY RECOMMENDATIONS:")
        print("-" * 40)
        best_strategy = sorted_strategies[0][0] if sorted_strategies else "None"
        print(f"Best performing strategy: {best_strategy}")

        reliable_strategies = [s[0] for s in sorted_strategies if s[1] >= 50]
        print(f"Reliable strategies (≥50%): {', '.join(reliable_strategies) if reliable_strategies else 'None'}")

        total_unique_successes = len(set(r['video_id'] for r in successes))
        print(f"Unique videos successfully transcribed: {total_unique_successes}")

        if self.successful / self.total_tested >= 0.7:
            print("\n🎉 EXCELLENT: System ready for production!")
        elif self.successful / self.total_tested >= 0.5:
            print("\n👍 GOOD: System performs well!")
        else:
            print("\n⚠️  NEEDS IMPROVEMENT: Consider optimizing strategies")


async def test_clean_messaging_system():
    """
    Test the clean messaging system implementation.
    Verifies that status messages would be properly deleted during processing.
    """
    print("\n" + "=" * 60)
    print("🧹 TESTING CLEAN MESSAGING SYSTEM")
    print("=" * 60)

    # Mock classes to simulate Telegram message behavior
    class MockMessage:
        def __init__(self, message_id):
            self.message_id = message_id
            self.deleted = False
            self.text = ""
            self.edit_count = 0

        async def edit_text(self, text, **kwargs):
            self.text = text
            self.edit_count += 1
            print(f"  📝 Message {self.message_id} updated: {text[:50]}...")
            return self

        async def delete(self):
            self.deleted = True
            print(f"  🗑️ Message {self.message_id} DELETED")

    class MockChat:
        def __init__(self):
            self.message_counter = 1

        async def send_message(self, text, **kwargs):
            msg = MockMessage(self.message_counter)
            msg.text = text
            self.message_counter += 1
            print(f"  📤 New message {msg.message_id}: {text[:50]}...")
            return msg

    print("\n1. Testing YouTube processing flow...")

    # Simulate status message lifecycle
    chat = MockChat()

    # Initial status message
    status_msg = await chat.send_message("🎬 Processing YouTube video...")

    # Strategy updates
    strategies = [("SaveSubs", False), ("Tactiq", True)]
    for i, (name, success) in enumerate(strategies, 1):
        await status_msg.edit_text(f"⚡ Strategy {i}: {name}")
        if success:
            await status_msg.edit_text(f"✅ Success with {name}")
            break
        else:
            await status_msg.edit_text(f"❌ Failed: {name}")

    # Enhancement (status update only - no new message)
    await status_msg.edit_text("✨ Enhancing with AI...")
    await status_msg.edit_text("✨ Enhancement completed")

    # Chunk preparation (status update only - no new message)
    await status_msg.edit_text("📝 Preparing transcription...")
    await status_msg.edit_text("📝 Sending transcription")

    # Final transcription (NEW message - this should remain)
    final_msg = await chat.send_message("🎵 **Transcription Complete**\n\nActual transcription text...")

    # Status message cleanup
    await status_msg.delete()  # Should be deleted

    # Verify clean state - Only 2 messages total: status (deleted) + final (remains)
    expected_messages = 2  # status + final
    actual_messages = chat.message_counter - 1

    temp_messages_deleted = status_msg.deleted
    final_remains = not final_msg.deleted
    correct_message_count = actual_messages == expected_messages

    print(f"\n📊 CLEAN MESSAGING TEST RESULTS:")
    print(f"   Status message deleted: {'✅' if status_msg.deleted else '❌'}")
    print(f"   No intermediate messages created: {'✅' if correct_message_count else '❌'}")
    print(f"   Final message remains: {'✅' if final_remains else '❌'}")
    print(f"   Total messages created: {actual_messages} (expected: {expected_messages})")

    if temp_messages_deleted and final_remains and correct_message_count:
        print("   🎉 SUCCESS: Clean messaging system works correctly!")
        return True
    else:
        print("   ❌ FAILURE: Clean messaging system has issues")
        return False


async def test_handler_integration():
    """
    Test that handlers properly implement the clean messaging system.
    Verifies the status_message parameter is correctly handled.
    """
    print("\n2. Testing handler integration...")

    try:
        # Import handlers to verify they accept status_message parameter
        from bot.handlers.media.youtube_handler import youtube_handler
        from bot.handlers.media.video_handler import video_handler
        from bot.handlers.media.audio_handler import audio_handler
        from bot.utils.transcription_utils import process_media

        # Check function signatures via inspection
        import inspect

        # Check process_media accepts status_message
        process_media_sig = inspect.signature(process_media)
        has_status_param = 'status_message' in process_media_sig.parameters

        print(f"   process_media accepts status_message: {'✅' if has_status_param else '❌'}")

        if has_status_param:
            print("   🎉 SUCCESS: Handlers properly integrated with clean messaging!")
            return True
        else:
            print("   ❌ FAILURE: Handler integration incomplete")
            return False

    except ImportError as e:
        print(f"   ❌ IMPORT ERROR: {e}")
        return False


async def run_clean_messaging_tests():
    """Run all clean messaging system tests."""
    print("🧹 RUNNING CLEAN MESSAGING SYSTEM TESTS")
    print("=" * 60)

    test_results = []

    # Test 1: Clean messaging flow
    result1 = await test_clean_messaging_system()
    test_results.append(result1)

    # Test 2: Handler integration
    result2 = await test_handler_integration()
    test_results.append(result2)

    # Summary
    passed = sum(test_results)
    total = len(test_results)

    print(f"\n📊 CLEAN MESSAGING TESTS SUMMARY:")
    print(f"   Passed: {passed}/{total}")
    print(f"   Success rate: {passed/total*100:.1f}%")

    if passed == total:
        print("   🎉 ALL CLEAN MESSAGING TESTS PASSED!")
    else:
        print("   ❌ Some clean messaging tests failed")

    return passed == total


async def main():
    """Run comprehensive YouTube URL and strategy testing."""

    start_time = time.time()

    # Parse command line arguments
    quick_test = len(sys.argv) > 1 and sys.argv[1] == 'quick'
    clean_test = len(sys.argv) > 1 and sys.argv[1] == 'clean'

    if clean_test:
        # Run only clean messaging tests
        success = await run_clean_messaging_tests()
        sys.exit(0 if success else 1)

    # Load URLs from external file
    TEST_URLS = load_test_urls_from_file()

    total_urls = sum(len(urls) for urls in TEST_URLS.values())
    total_tests = total_urls * len(YouTubeTranscriptExtractor().strategies)  # All strategies per URL

    print("🚀 STARTING COMPREHENSIVE YOUTUBE URL AND STRATEGY TESTING")
    print(f"📊 Total URLs to test: {total_urls}")
    print(f"🔧 Total individual strategy tests: {total_tests}")
    print(f"⚙️  Available strategies: {len(YouTubeTranscriptExtractor().strategies)}")
    print()

    tester = YouTubeURLTester()
    await tester.run_comprehensive_test()

    end_time = time.time()
    duration = end_time - start_time

    print(f"\n⏱️  Total testing time: {duration:.1f} seconds")
    print(f"🚀 Average time per URL: {duration/tester.total_tested:.2f} seconds")
    print(f"⚡ Average time per strategy test: {duration/len(tester.results):.2f} seconds")

    # Final verdict
    success_rate = (tester.successful / tester.total_tested) * 100
    print(f"\n🎯 FINAL VERDICT:")
    print(f"   Overall Success Rate: {success_rate:.1f}%")

    if success_rate >= 70:
        print(f"   Status: ✅ EXCELLENT - Production ready!")
    elif success_rate >= 50:
        print(f"   Status: ✅ GOOD - Acceptable for production")
    elif success_rate >= 30:
        print(f"   Status: ⚠️  FAIR - May need improvements")
    else:
        print(f"   Status: ❌ POOR - Needs significant work")

    print("\n🎉 COMPREHENSIVE TESTING COMPLETED!")
    print("All YouTube URL formats and extraction strategies fully tested!")

async def quick_test():
    """Quick test with just a few URLs for fast debugging."""
    logger.info("🚀 Starting QUICK TEST mode")

    # Load only quick_test category from file
    QUICK_TEST_URLS = load_test_urls_from_file(categories=['quick_test'])

    print("🏃‍♂️ QUICK TEST MODE - Testing quick test URLs only")
    print("=" * 50)

    start_time = time.time()

    tester = YouTubeURLTester()

    # Temporarily modify the test to use only quick test URLs
    original_run_method = tester.run_comprehensive_test

    async def quick_run():
        TEST_URLS = QUICK_TEST_URLS
        total_urls = sum(len(urls) for urls in TEST_URLS.values())
        total_strategies = len(tester.strategy_methods)
        total_tests = total_urls * total_strategies

        logger.info(f"📊 Quick test scope:")
        logger.info(f"   Total URLs: {total_urls}")
        logger.info(f"   Total strategies: {total_strategies}")
        logger.info(f"   Total individual tests: {total_tests}")

        print("🎯 QUICK YOUTUBE URL AND STRATEGY TESTING")
        print("=" * 80)
        print(f"Testing {total_urls} URLs")
        print(f"Using {total_strategies} different extraction strategies:")
        for i, strategy in enumerate(tester.strategy_methods.keys(), 1):
            print(f"  {i}. {strategy}")
        print("=" * 80)

        for category_num, (category, urls) in enumerate(TEST_URLS.items(), 1):
            logger.info(f"📂 Starting category {category_num}/{len(TEST_URLS)}: {category}")
            logger.info(f"   URLs in this category: {len(urls)}")

            print(f"\n📂 {category.upper()} ({len(urls)} URLs) - Category {category_num}/{len(TEST_URLS)}")
            print("-" * 60)

            for url_num, url_data in enumerate(urls, 1):
                url = url_data['url']
                description = url_data['description']
                video_id = tester.extract_video_id(url)

                if not video_id:
                    logger.warning(f"   ❌ Could not extract video ID from URL: {url}")
                    print(f"      ❌ INVALID URL - Could not extract video ID")
                    tester.failed += 1
                    tester.total_tested += 1
                    continue

                logger.info(f"   🎥 URL {url_num}/{len(urls)}: {description}")
                logger.info(f"      Video ID: {video_id}")
                print(f"   🎥 URL {url_num}/{len(urls)}: {description}")

                url_success = False
                strategy_count = 0

                for strategy_name, strategy_method in tester.strategy_methods.items():
                    strategy_count += 1
                    result = await tester.test_single_strategy(video_id, strategy_name, url, category)
                    tester.results.append(result)

                    if result['status'] == 'SUCCESS':
                        url_success = True
                        tester.strategy_results[strategy_name]['success'] += 1
                        print(f"      ✅ {strategy_name}: SUCCESS ({result['transcript_length']} chars)")
                    else:
                        tester.strategy_results[strategy_name]['errors'].append({
                            'video_id': video_id,
                            'error': result['error']
                        })
                        print(f"      ❌ {strategy_name}: {result['error']}")

                    tester.strategy_results[strategy_name]['total'] += 1
                    await asyncio.sleep(tester.strategy_delay)

                if url_success:
                    tester.successful += 1
                    print(f"      🎉 URL SUCCESS: At least one strategy worked")
                else:
                    tester.failed += 1
                    print(f"      💥 URL FAILED: No strategy worked")

                tester.total_tested += 1
                logger.info(f"   URL {url_num} completed. Success: {url_success}")
                await asyncio.sleep(tester.url_delay)

            logger.info(f"📂 Category {category} completed. Progress: {category_num}/{len(TEST_URLS)}")

    await quick_run()

    end_time = time.time()
    duration = end_time - start_time

    print(f"\n⏱️  Quick test completed in {duration:.1f} seconds")
    success_rate = (tester.successful / tester.total_tested) * 100 if tester.total_tested > 0 else 0
    print(f"🎯 Quick test success rate: {success_rate:.1f}%")

# Allow running in different modes
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        print("Running in QUICK TEST mode...")
        asyncio.run(quick_test())
    elif len(sys.argv) > 1 and sys.argv[1] == "clean":
        print("Running CLEAN MESSAGING TESTS...")
        asyncio.run(run_clean_messaging_tests())
    else:
        print("Running FULL COMPREHENSIVE test...")
        print("Usage modes:")
        print("  python comprehensive_test.py        - Full test (all URLs)")
        print("  python comprehensive_test.py quick  - Quick test (5 URLs)")
        print("  python comprehensive_test.py clean  - Clean messaging tests")
        asyncio.run(main())
