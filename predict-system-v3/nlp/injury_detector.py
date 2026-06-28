import spacy
from datetime import datetime
from sqlalchemy.orm import Session
from database import Player, InjuryReport
import trafilatura
import logging

logger = logging.getLogger(__name__)

class InjuryDetector:
    """
    Phase 3.1: NLP injury/suspension detector using spaCy NER.
    Scans news articles to find Player Name + injured/suspended/doubtful.
    """
    
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("Loaded spaCy model en_core_web_sm")
        except:
            logger.warning("spaCy model not found, injury detection will use pattern matching")
            self.nlp = None
        
        self.injury_keywords = [
            'injured', 'injury', 'hurt', 'suspended', 'suspension',
            'doubtful', 'sidelined', 'ruled out', 'unavailable',
            'fitness concern', 'knee injury', 'hamstring', 'ankle'
        ]
        logger.info("InjuryDetector initialized")
    
    def scan_news_article(self, url: str, db: Session):
        """
        Scan a news article for injury/suspension mentions.
        """
        logger.info(f"Scanning news article: {url}")
        
        try:
            text = trafilatura.fetch_url(url)
            if not text:
                logger.warning(f"Failed to fetch content from {url}")
                return []
            
            content = trafilatura.extract(text)
            if not content:
                logger.warning(f"Failed to extract text from {url}")
                return []
            
            injuries = self._detect_injuries(content, db)
            logger.info(f"Detected {len(injuries)} injury mentions in article")
            return injuries
            
        except Exception as e:
            logger.error(f"Error scanning news article: {e}")
            return []
    
    def _detect_injuries(self, text: str, db: Session):
        """
        Detect injury mentions in text using NER and pattern matching.
        """
        injuries = []
        
        sentences = text.split('.')
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            has_injury_keyword = any(keyword in sentence_lower for keyword in self.injury_keywords)
            
            if has_injury_keyword:
                if self.nlp:
                    doc = self.nlp(sentence)
                    for ent in doc.ents:
                        if ent.label_ == "PERSON":
                            player = db.query(Player).filter(
                                Player.name.ilike(f"%{ent.text}%")
                            ).first()
                            
                            if player:
                                status = self._determine_injury_status(sentence_lower)
                                severity = self._determine_severity(sentence_lower)
                                
                                injuries.append({
                                    'player_id': player.id,
                                    'player_name': player.name,
                                    'status': status,
                                    'severity': severity,
                                    'detection_source': 'NLP_news_scan',
                                    'confidence_score': 0.75
                                })
        
        return injuries
    
    def _determine_injury_status(self, text: str):
        """
        Determine injury status from text.
        """
        if 'suspended' in text or 'suspension' in text:
            return 'suspended'
        elif 'injured' in text or 'injury' in text:
            return 'injured'
        elif 'doubtful' in text or 'concern' in text:
            return 'doubtful'
        else:
            return 'injured'
    
    def _determine_severity(self, text: str):
        """
        Determine injury severity from text.
        """
        if any(word in text for word in ['serious', 'severe', 'major', 'season-ending']):
            return 'severe'
        elif any(word in text for word in ['minor', 'slight', 'knock']):
            return 'minor'
        else:
            return 'moderate'
    
    def save_injury_report(self, injury_data: dict, db: Session):
        """
        Save injury report to database.
        """
        try:
            report = InjuryReport(
                player_id=injury_data['player_id'],
                status=injury_data['status'],
                severity=injury_data.get('severity'),
                injury_type=injury_data.get('injury_type'),
                detection_source=injury_data['detection_source'],
                report_date=datetime.utcnow(),
                is_active=True,
                confidence_score=injury_data.get('confidence_score', 0.5)
            )
            db.add(report)
            db.commit()
            logger.info(f"Saved injury report for player {injury_data['player_name']}")
            return True
        except Exception as e:
            logger.error(f"Error saving injury report: {e}")
            db.rollback()
            return False
