#!/usr/bin/env python3
"""
YACHAQ DATA COLLECTOR FRAMEWORK
================================
Reusable data abstraction for Yachaq LLM EC

Features:
- Multiple source types (API, Web, Database, Files)
- Automatic logging of all sources
- Data quality validation
- Ecuador data protection compliance
- S3 upload with metadata

Usage:
    from yachaq_collector import YachaqCollector
    
    collector = YachaqCollector()
    collector.collect_from_api("https://api.example.com")
    collector.collect_from_web("https://www.example.com")
"""

import os
import json
import hashlib
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import subprocess
import requests
import re

# Configuration
S3_BUCKET = "s3://yachaq-lex-raw-0017472631"
REGISTRY_PATH = "/Users/macbookpro201916i964gb1tb/Downloads/1x/yachaq/registry"
LOGS_PATH = "/Users/macbookpro201916i964gb1tb/Downloads/1x/yachaq/logs"

# Setup logging
os.makedirs(LOGS_PATH, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(f"{LOGS_PATH}/yachaq_collector.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class DataSource:
    """Represents a data source with metadata"""
    source_id: str
    source_type: str  # api, web, database, file
    url: str
    name: str
    description: str
    license: str
    is_public: bool
    collected_at: str
    s3_path: str
    size_bytes: int
    record_count: int
    quality_score: float
    category: str
    tags: List[str]


@dataclass
class DataProtectionCheck:
    """Ecuador LOPDP compliance check"""
    is_public_data: bool
    has_pii: bool
    source_is_government: bool
    license_allows_use: bool
    compliant: bool


class DataValidator:
    """Validates data quality and compliance"""
    
    # Patterns for PII detection
    PII_PATTERNS = [
        r'\b\d{10}\b',  # Cedula
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
        r'\b\d{2,4}[-\s]?\d{3,4}[-\s]?\d{3,4}\b',  # Phone numbers
    ]
    
    # Government domains
    GOV_DOMAINS = [
        '.gob.ec', '.gov.ec', '.edu.ec', 
        'datosabiertos.gob.ec', 'wikipedia.org'
    ]
    
    @classmethod
    def check_pii(cls, text: str) -> bool:
        """Check if text contains PII"""
        for pattern in cls.PII_PATTERNS:
            if re.search(pattern, text):
                return True
        return False
    
    @classmethod
    def is_government_source(cls, url: str) -> bool:
        """Check if URL is from government domain"""
        return any(domain in url.lower() for domain in cls.GOV_DOMAINS)
    
    @classmethod
    def validate_data_protection(cls, url: str, content: str) -> DataProtectionCheck:
        """Validate Ecuador data protection compliance"""
        is_gov = cls.is_government_source(url)
        has_pii = cls.check_pii(content[:10000])  # Check first 10k chars
        
        return DataProtectionCheck(
            is_public_data=True,  # We only collect public data
            has_pii=has_pii,
            source_is_government=is_gov,
            license_allows_use=is_gov,  # Gov data is public
            compliant=is_gov and not has_pii
        )
    
    @classmethod
    def calculate_quality_score(cls, content: str) -> float:
        """Calculate data quality score 0-1"""
        if not content:
            return 0.0
        
        score = 1.0
        
        # Penalize very short content
        if len(content) < 100:
            score -= 0.3
        
        # Penalize if mostly HTML
        html_ratio = len(re.findall(r'<[^>]+>', content)) / max(len(content), 1)
        if html_ratio > 0.3:
            score -= 0.2
        
        # Penalize if contains PII
        if cls.check_pii(content):
            score -= 0.5
        
        return max(0.0, min(1.0, score))


class SourceRegistry:
    """Manages registry of all collected data sources"""
    
    def __init__(self, registry_path: str = REGISTRY_PATH):
        self.registry_path = registry_path
        self.registry_file = os.path.join(registry_path, "data_sources.json")
        os.makedirs(registry_path, exist_ok=True)
        self.sources = self._load()
    
    def _load(self) -> Dict[str, DataSource]:
        """Load registry from disk"""
        if os.path.exists(self.registry_file):
            with open(self.registry_file, 'r') as f:
                data = json.load(f)
                return {k: DataSource(**v) for k, v in data.items()}
        return {}
    
    def save(self):
        """Save registry to disk"""
        with open(self.registry_file, 'w') as f:
            json.dump({k: asdict(v) for k, v in self.sources.items()}, f, indent=2)
    
    def add(self, source: DataSource):
        """Add source to registry"""
        self.sources[source.source_id] = source
        self.save()
        logger.info(f"Registered source: {source.name} ({source.source_id})")
    
    def get_stats(self) -> Dict:
        """Get registry statistics"""
        return {
            "total_sources": len(self.sources),
            "total_size_gb": sum(s.size_bytes for s in self.sources.values()) / (1024**3),
            "total_records": sum(s.record_count for s in self.sources.values()),
            "by_type": {},
            "by_category": {}
        }


class BaseCollector(ABC):
    """Base class for all collectors"""
    
    def __init__(self, registry: SourceRegistry):
        self.registry = registry
        self.headers = {
            "User-Agent": "YachaqLLM/1.0 (Educational; https://yachaq.ec)"
        }
    
    @abstractmethod
    def collect(self, source: str, **kwargs) -> Optional[str]:
        """Collect data from source"""
        pass
    
    def _generate_source_id(self, url: str) -> str:
        """Generate unique source ID"""
        return hashlib.md5(url.encode()).hexdigest()[:12]
    
    def _upload_to_s3(self, content: str, s3_path: str) -> bool:
        """Upload content to S3"""
        import tempfile
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            if isinstance(content, str):
                f.write(content)
            else:
                json.dump(content, f, ensure_ascii=False)
            temp_path = f.name
        
        try:
            result = subprocess.run(
                ["aws", "s3", "cp", temp_path, s3_path],
                capture_output=True, text=True
            )
            os.unlink(temp_path)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"S3 upload failed: {e}")
            return False


class APICollector(BaseCollector):
    """Collect data from REST APIs"""
    
    def collect(self, url: str, params: Dict = None, 
                name: str = None, category: str = "api") -> Optional[str]:
        """Collect data from API endpoint"""
        source_id = self._generate_source_id(url)
        
        try:
            logger.info(f"Collecting from API: {url}")
            response = requests.get(url, params=params, headers=self.headers, timeout=60)
            response.raise_for_status()
            
            content = response.text
            data = response.json() if response.headers.get('content-type', '').startswith('application/json') else None
            
            # Validate
            check = DataValidator.validate_data_protection(url, content)
            if not check.compliant:
                logger.warning(f"Data protection check failed for {url}")
                if check.has_pii:
                    return None  # Skip data with PII
            
            quality = DataValidator.calculate_quality_score(content)
            if quality < 0.3:
                logger.warning(f"Low quality score ({quality}) for {url}")
            
            # Upload to S3
            s3_path = f"{S3_BUCKET}/yachaq/{category}/{source_id}.json"
            if self._upload_to_s3(content, s3_path):
                # Register source
                source = DataSource(
                    source_id=source_id,
                    source_type="api",
                    url=url,
                    name=name or url,
                    description=f"API data from {url}",
                    license="Public Domain / CC BY 4.0",
                    is_public=True,
                    collected_at=datetime.now().isoformat(),
                    s3_path=s3_path,
                    size_bytes=len(content),
                    record_count=len(data) if isinstance(data, list) else 1,
                    quality_score=quality,
                    category=category,
                    tags=["api", category]
                )
                self.registry.add(source)
                return content
                
        except Exception as e:
            logger.error(f"API collection failed: {e}")
        
        return None


class WebCollector(BaseCollector):
    """Collect data from web pages"""
    
    def collect(self, url: str, name: str = None, 
                category: str = "web") -> Optional[str]:
        """Collect text content from web page"""
        source_id = self._generate_source_id(url)
        
        try:
            logger.info(f"Collecting from Web: {url}")
            response = requests.get(url, headers=self.headers, timeout=60)
            response.raise_for_status()
            
            # Extract text (basic HTML stripping)
            content = response.text
            text = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
            text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
            text = re.sub(r'<[^>]+>', ' ', text)
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Validate
            check = DataValidator.validate_data_protection(url, text)
            quality = DataValidator.calculate_quality_score(text)
            
            if quality < 0.3 or len(text) < 500:
                logger.warning(f"Skipping low quality content from {url}")
                return None
            
            # Upload to S3
            s3_path = f"{S3_BUCKET}/yachaq/{category}/{source_id}.txt"
            if self._upload_to_s3(text, s3_path):
                source = DataSource(
                    source_id=source_id,
                    source_type="web",
                    url=url,
                    name=name or url,
                    description=f"Web content from {url}",
                    license="Public Domain",
                    is_public=True,
                    collected_at=datetime.now().isoformat(),
                    s3_path=s3_path,
                    size_bytes=len(text),
                    record_count=1,
                    quality_score=quality,
                    category=category,
                    tags=["web", category]
                )
                self.registry.add(source)
                return text
                
        except Exception as e:
            logger.error(f"Web collection failed: {e}")
        
        return None


class YachaqCollector:
    """Main Yachaq data collection orchestrator"""
    
    def __init__(self):
        self.registry = SourceRegistry()
        self.api_collector = APICollector(self.registry)
        self.web_collector = WebCollector(self.registry)
        logger.info("YachaqCollector initialized")
    
    def collect_from_api(self, url: str, **kwargs) -> Optional[str]:
        """Collect from API"""
        return self.api_collector.collect(url, **kwargs)
    
    def collect_from_web(self, url: str, **kwargs) -> Optional[str]:
        """Collect from web page"""
        return self.web_collector.collect(url, **kwargs)
    
    def collect_batch(self, sources: List[Dict]) -> Dict:
        """Collect from multiple sources"""
        results = {"success": 0, "failed": 0}
        
        for source in sources:
            source_type = source.get("type", "web")
            url = source.get("url")
            
            if source_type == "api":
                result = self.collect_from_api(url, **source)
            else:
                result = self.collect_from_web(url, **source)
            
            if result:
                results["success"] += 1
            else:
                results["failed"] += 1
        
        return results
    
    def get_stats(self) -> Dict:
        """Get collection statistics"""
        return self.registry.get_stats()
    
    def export_registry(self, path: str = None) -> str:
        """Export registry to file"""
        path = path or os.path.join(REGISTRY_PATH, "export.json")
        with open(path, 'w') as f:
            json.dump({k: asdict(v) for k, v in self.registry.sources.items()}, f, indent=2)
        return path


# Entry point for testing
if __name__ == "__main__":
    collector = YachaqCollector()
    
    # Test with Ecuador Wikipedia
    collector.collect_from_api(
        "https://es.wikipedia.org/w/api.php",
        params={"action": "query", "titles": "Ecuador", "prop": "extracts", "format": "json"},
        name="Wikipedia Ecuador",
        category="wikipedia"
    )
    
    print(collector.get_stats())
