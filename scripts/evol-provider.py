#!/usr/bin/env python3
"""Evol-DD LLM Provider Abstraction"""
import os, sys, json

class MockProvider:
    """Deterministic mock — no network, for testing/CI."""
    
    def complete(self, prompt, system=None, max_tokens=1000):
        return {
            "content": f"[MOCK RESPONSE to: {prompt[:50]}...]",
            "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            "model": "mock"
        }

class AnthropicProvider:
    """Lazy Anthropic provider — requires ANTHROPIC_API_KEY."""
    
    def __init__(self):
        self.api_key = os.environ.get("ANTHROPIC_API_KEY")
        self.client = None
    
    def _ensure_client(self):
        if not self.client:
            try:
                import anthropic
                if not self.api_key:
                    raise ValueError("ANTHROPIC_API_KEY not set")
                self.client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                raise RuntimeError("anthropic package not installed")
    
    def complete(self, prompt, system=None, max_tokens=1000):
        self._ensure_client()
        resp = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": prompt}]
        )
        return {
            "content": resp.content[0].text,
            "usage": dict(resp.usage._raw),
            "model": resp.model
        }

def get_provider():
    mode = os.environ.get("EVOL_PROVIDER", "mock")
    if mode == "anthropic":
        return AnthropicProvider()
    return MockProvider()

def main():
    import argparse
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd")
    p = sub.add_parser("complete", help="Test completion")
    p.add_argument("--prompt", required=True)
    p.add_argument("--system", default=None)
    args = parser.parse_args()
    
    if args.cmd == "complete":
        prov = get_provider()
        result = prov.complete(args.prompt, args.system)
        print(result["content"])

if __name__ == "__main__":
    main()
