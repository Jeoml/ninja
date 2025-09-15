"""
Simulate a complete Round 2 quiz session.
Tests the depth of knowledge on strong topics from Round 1 using medium difficulty questions.
"""
import sys
import os
import requests
import json
import random
import time
from typing import List, Dict, Any

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_agents.round2.quiz_service import Round2QuizService

# Configuration
BASE_URL = "http://localhost:8000"
ROUND2_BASE = f"{BASE_URL}/ai-agents/round2"

# Simulation settings
MAX_QUESTIONS = 10
SIMULATED_ACCURACY = 0.75  # 75% accuracy for realistic simulation
DELAY_BETWEEN_QUESTIONS = 1  # seconds

# Sample Round 1 strong topics for simulation (actual topics from database)
SAMPLE_ROUND1_STRONG_TOPICS = [
    "Formulas", "Data", "Charts", "Text Functions", "Data Analysis", 
    "Conditional Formatting", "Formatting", "Shortcuts", "General"
]

class Round2Simulator:
    """Simulator for Round 2 quiz sessions."""
    
    def __init__(self):
        self.session_data = {}
        self.questions_answered = 0
        self.correct_answers = 0
        self.performance_by_topic = {}
        
    def check_server_health(self) -> bool:
        """Check if the Round 2 server is running and healthy."""
        try:
            print("🔍 Checking Round 2 server health...")
            response = requests.get(f"{ROUND2_BASE}/health", timeout=5)
            
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Round 2 server is healthy")
                print(f"   Medium questions available: {health_data['data']['medium_questions_available']}")
                print(f"   Topics available: {health_data['data']['topics_available']}")
                return True
            else:
                print(f"❌ Round 2 server health check failed: {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to Round 2 server. Make sure it's running on localhost:8000")
            return False
        except Exception as e:
            print(f"❌ Error checking Round 2 server health: {e}")
            return False
    
    def get_database_stats(self) -> Dict:
        """Get Round 2 database statistics."""
        try:
            print("\n📊 Getting Round 2 database statistics...")
            response = requests.get(f"{ROUND2_BASE}/database-stats")
            
            if response.status_code == 200:
                stats = response.json()["data"]
                print(f"   Total medium questions: {stats['total_medium_questions']}")
                print(f"   Available topics: {stats['available_medium_topics']}")
                print(f"   Top topics by question count:")
                for topic_info in stats['topic_distribution'][:5]:
                    print(f"     - {topic_info['topic']}: {topic_info['count']} questions")
                return stats
            else:
                print(f"❌ Failed to get database stats: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ Error getting database stats: {e}")
            return {}
    
    def start_round2_session(self, round1_strong_topics: List[str]) -> bool:
        """Start a Round 2 quiz session."""
        try:
            print(f"\n🚀 Starting Round 2 session...")
            print(f"   Round 1 strong topics: {round1_strong_topics}")
            print(f"   Max questions: {MAX_QUESTIONS}")
            
            payload = {
                "max_questions": MAX_QUESTIONS,
                "round1_strong_topics": round1_strong_topics,
                "user_email": "simulator@example.com"
            }
            
            response = requests.post(f"{ROUND2_BASE}/start", json=payload)
            
            if response.status_code == 200:
                self.session_data = response.json()["data"]
                strategy = self.session_data.get("strategy", "unknown")
                description = self.session_data.get("strategy_description", "")
                
                print(f"✅ Round 2 session started successfully!")
                print(f"   Strategy: {strategy}")
                print(f"   Description: Testing {description}")
                print(f"   Available questions: {self.session_data.get('available_questions', 0)}")
                return True
            else:
                error_detail = response.json().get("detail", "Unknown error")
                print(f"❌ Failed to start Round 2 session: {error_detail}")
                return False
                
        except Exception as e:
            print(f"❌ Error starting Round 2 session: {e}")
            return False
    
    def get_next_question(self) -> Dict[str, Any]:
        """Get the next Round 2 question."""
        try:
            response = requests.get(f"{ROUND2_BASE}/question")
            
            if response.status_code == 200:
                return response.json()["data"]
            else:
                error_detail = response.json().get("detail", "Unknown error")
                print(f"❌ Failed to get next question: {error_detail}")
                return {}
                
        except Exception as e:
            print(f"❌ Error getting next question: {e}")
            return {}
    
    def submit_answer(self, user_answer: str) -> Dict[str, Any]:
        """Submit an answer for the current Round 2 question."""
        try:
            payload = {"answer": user_answer}
            response = requests.post(f"{ROUND2_BASE}/answer", json=payload)
            
            if response.status_code == 200:
                return response.json()["data"]
            else:
                error_detail = response.json().get("detail", "Unknown error")
                print(f"❌ Failed to submit answer: {error_detail}")
                return {}
                
        except Exception as e:
            print(f"❌ Error submitting answer: {e}")
            return {}
    
    def simulate_user_answer(self, question_data: Dict) -> str:
        """Simulate a user's answer based on configured accuracy."""
        options = ["A", "B", "C", "D"]
        
        # Simulate accuracy - sometimes give correct answer, sometimes random
        if random.random() < SIMULATED_ACCURACY:
            # For simulation, we don't have access to correct answer from API
            # So we'll use a smarter random selection based on topic difficulty
            topic = question_data.get("topic", "")
            from_round1_strength = question_data.get("from_round1_strength", False)
            
            # Higher chance of correct answer for topics from Round 1 strengths
            if from_round1_strength:
                # Simulate 85% accuracy on Round 1 strength topics
                if random.random() < 0.85:
                    # Pick a "smart" answer (first or second option more likely to be correct)
                    return random.choices(options, weights=[0.4, 0.3, 0.2, 0.1])[0]
            else:
                # Simulate 65% accuracy on new topics
                if random.random() < 0.65:
                    return random.choices(options, weights=[0.3, 0.3, 0.25, 0.15])[0]
        
        # Random guess
        return random.choice(options)
    
    def run_complete_round2_simulation(self, round1_strong_topics: List[str]) -> bool:
        """Run a complete Round 2 simulation."""
        print("=" * 60)
        print("🎯 ROUND 2 SIMULATION - TESTING DEPTH OF KNOWLEDGE")
        print("=" * 60)
        
        # Check server health
        if not self.check_server_health():
            return False
        
        # Get database stats
        self.get_database_stats()
        
        # Start Round 2 session
        if not self.start_round2_session(round1_strong_topics):
            return False
        
        # Add small delay to ensure session is established
        time.sleep(0.5)
        
        print(f"\n🎮 Starting Round 2 quiz simulation...")
        print(f"   Target accuracy: {SIMULATED_ACCURACY * 100:.0f}%")
        print("-" * 50)
        
        # Answer questions until completion
        question_count = 0
        while question_count < MAX_QUESTIONS:
            # Get next question
            question_data = self.get_next_question()
            
            if not question_data:
                print("❌ No more questions available or session ended")
                break
            
            question_count += 1
            topic = question_data.get("topic", "Unknown")
            from_round1 = question_data.get("from_round1_strength", False)
            strength_indicator = "💪" if from_round1 else "🆕"
            
            print(f"\n📝 Question {question_count}/{MAX_QUESTIONS} {strength_indicator}")
            print(f"   Topic: {topic}")
            print(f"   From Round 1 strength: {from_round1}")
            print(f"   Question: {question_data.get('question', '')[:100]}...")
            
            # Show options
            options = question_data.get("options", {})
            for letter, option in options.items():
                print(f"   {letter}) {option[:80]}...")
            
            # Simulate user thinking time
            time.sleep(DELAY_BETWEEN_QUESTIONS)
            
            # Generate simulated answer
            user_answer = self.simulate_user_answer(question_data)
            print(f"   🤖 Simulated answer: {user_answer}")
            
            # Submit answer
            answer_result = self.submit_answer(user_answer)
            
            if answer_result:
                is_correct = answer_result.get("is_correct", False)
                correct_answer = answer_result.get("correct_answer", "?")
                
                if is_correct:
                    print(f"   ✅ Correct! ({correct_answer})")
                    self.correct_answers += 1
                else:
                    print(f"   ❌ Incorrect. Correct answer was: {correct_answer}")
                
                # Track performance by topic
                if topic not in self.performance_by_topic:
                    self.performance_by_topic[topic] = {"correct": 0, "total": 0}
                
                self.performance_by_topic[topic]["total"] += 1
                if is_correct:
                    self.performance_by_topic[topic]["correct"] += 1
                
                self.questions_answered += 1
                
                # Show quiz completion status
                if answer_result.get("quiz_completed", False):
                    print(f"\n🎉 Round 2 completed!")
                    self.show_final_results(answer_result.get("final_results", {}))
                    break
                else:
                    remaining = answer_result.get("questions_remaining", 0)
                    print(f"   Questions remaining: {remaining}")
        
        return True
    
    def show_final_results(self, final_results: Dict):
        """Display final Round 2 results."""
        print("\n" + "=" * 60)
        print("🏆 ROUND 2 FINAL RESULTS")
        print("=" * 60)
        
        # Overall performance
        total_questions = final_results.get("total_questions", 0)
        correct = final_results.get("correct_answers", 0)
        accuracy = final_results.get("accuracy", 0.0)
        
        print(f"📊 Overall Performance:")
        print(f"   Questions answered: {total_questions}")
        print(f"   Correct answers: {correct}")
        print(f"   Accuracy: {accuracy:.1%}")
        
        # Topic performance levels
        expert_topics = final_results.get("expert_topics", [])
        proficient_topics = final_results.get("proficient_topics", [])
        developing_topics = final_results.get("developing_topics", [])
        struggling_topics = final_results.get("struggling_topics", [])
        crazy_good_topics = final_results.get("crazy_good_topics", [])
        
        print(f"\n🎯 Topic Performance Levels:")
        print(f"   🌟 EXPERT (80%+): {expert_topics if expert_topics else 'None'}")
        print(f"   💪 PROFICIENT (60-79%): {proficient_topics if proficient_topics else 'None'}")
        print(f"   📈 DEVELOPING (40-59%): {developing_topics if developing_topics else 'None'}")
        print(f"   📚 STRUGGLING (<40%): {struggling_topics if struggling_topics else 'None'}")
        
        print(f"\n🚀 CRAZY GOOD TOPICS: {crazy_good_topics if crazy_good_topics else 'None'}")
        
        # Round 1 progression analysis
        round1_progression = final_results.get("round1_progression", {})
        if round1_progression:
            print(f"\n🔄 Round 1 → Round 2 Progression:")
            for topic, progression in round1_progression.items():
                status = progression.get("round2_status", "unknown")
                maintained = progression.get("maintained_strength", False)
                indicator = "✅" if maintained else "⚠️"
                print(f"   {indicator} {topic}: {status}")
        
        # Topic breakdown
        topic_breakdown = final_results.get("topic_breakdown", {})
        if topic_breakdown:
            print(f"\n📋 Detailed Topic Breakdown:")
            for topic, stats in topic_breakdown.items():
                correct = stats.get("correct", 0)
                total = stats.get("total", 0)
                accuracy = stats.get("accuracy", 0.0)
                status = stats.get("status", "unknown")
                from_round1 = stats.get("from_round1_strength", False)
                origin = "💪 Round 1 strength" if from_round1 else "🆕 New exploration"
                
                print(f"   {topic}: {correct}/{total} ({accuracy:.1%}) - {status} - {origin}")
        
        # Recommendations
        if len(crazy_good_topics) >= 3:
            print(f"\n🎓 RECOMMENDATION: Ready for Round 3! You've shown expertise in multiple areas.")
        elif len(crazy_good_topics) >= 1:
            print(f"\n📈 RECOMMENDATION: Good progress! Continue building depth in your strong areas.")
        else:
            print(f"\n📚 RECOMMENDATION: Focus on strengthening foundational knowledge before advancing.")
        
        print("\n" + "=" * 60)

def get_realistic_round1_topics() -> List[str]:
    """Get realistic Round 1 strong topics from actual database topics."""
    try:
        # Import here to avoid circular imports
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from ai_agents.round1.database_service import DatabaseService
        from ai_agents.round2.database_service import Round2DatabaseService
        
        # Get topics that exist in both easy and medium difficulties
        easy_topics = DatabaseService.get_all_topics()
        medium_topics = Round2DatabaseService.get_all_medium_topics()
        
        # Find overlap - topics that have both easy and medium questions
        overlapping_topics = list(set(easy_topics) & set(medium_topics))
        
        if len(overlapping_topics) >= 2:
            # Select 2-4 topics that have both easy and medium questions
            return random.sample(overlapping_topics, k=min(len(overlapping_topics), random.randint(2, 4)))
        else:
            # Fallback to any available topics
            available_topics = easy_topics if easy_topics else SAMPLE_ROUND1_STRONG_TOPICS
            return random.sample(available_topics, k=min(len(available_topics), random.randint(2, 4)))
            
    except Exception as e:
        print(f"⚠️  Error getting realistic topics: {e}")
        # Fallback to sample topics
        return random.sample(SAMPLE_ROUND1_STRONG_TOPICS, k=random.randint(2, 4))

def main():
    """Main simulation function."""
    print("🎯 Round 2 Quiz Simulation")
    print("Testing depth of knowledge with medium difficulty questions")
    
    # Create simulator
    simulator = Round2Simulator()
    
    # Get realistic Round 1 strong topics from actual database
    print("🔍 Getting realistic Round 1 strong topics from database...")
    round1_topics = get_realistic_round1_topics()
    print(f"📋 Selected Round 1 strong topics: {round1_topics}")
    
    # Run the simulation
    success = simulator.run_complete_round2_simulation(round1_topics)
    
    if success:
        print(f"\n✅ Round 2 simulation completed successfully!")
        print(f"   Questions answered: {simulator.questions_answered}")
        print(f"   Correct answers: {simulator.correct_answers}")
        if simulator.questions_answered > 0:
            actual_accuracy = simulator.correct_answers / simulator.questions_answered
            print(f"   Actual accuracy: {actual_accuracy:.1%}")
    else:
        print(f"\n❌ Round 2 simulation failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
