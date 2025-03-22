import concurrent.futures

from .apis.anthropic import claude_count_tokens


def count_tokens_in_text(text, chunk_size=5_000_000):
    """Count tokens in a text by chunking and parallel processing."""
    # Split text into chunks
    chunks = [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]

    # Process chunks in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        token_counts = list(executor.map(claude_count_tokens, chunks))

    return sum(token_counts)


def analyze_corpus_tokens(texts):
    """Analyze token and character counts for a corpus of texts."""
    total_text = " ".join(texts)
    print(f"Total characters: {len(total_text):,}")
    print(f"Total tokens: {count_tokens_in_text(total_text):,}")
