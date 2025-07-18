import json
import os

class DatabaseManager:
    def __init__(self):
        self.scores_file = "highscores.json"
        
    async def initialize(self):
        """Initialize database connection"""
        pass
    
    async def get_high_scores(self):
        """Load high scores from JSON file"""
        try:
            if os.path.exists(self.scores_file):
                with open(self.scores_file, 'r') as f:
                    scores_data = json.load(f)
                    # Handle both old format (just scores) and new format (with names)
                    if scores_data and isinstance(scores_data[0], dict):
                        return scores_data
                    else:
                        return [{"name": "Anonymous", "score": score} for score in scores_data]
            return []
        except:
            return []
    
    async def save_score(self, player_name: str, score: int):
        """Save a new score to JSON file"""
        try:
            scores = []
            if os.path.exists(self.scores_file):
                with open(self.scores_file, 'r') as f:
                    existing_data = json.load(f)
                    # Convert old format if needed
                    if existing_data and isinstance(existing_data[0], dict):
                        scores = existing_data
                    else:
                        scores = [{"name": "Anonymous", "score": s} for s in existing_data]
            
            scores.append({"name": player_name, "score": score})
            scores.sort(key=lambda x: x["score"], reverse=True)
            scores = scores[:5]  # Keep only top 5
            
            with open(self.scores_file, 'w') as f:
                json.dump(scores, f)
            return True
        except:
            return False
