"""
Simulate a complete Round 1 quiz session.
Shows the full flow from start to finish with user's strengths catalog.
"""
import sys
import os
import time
import random

# Add the project root to Python path (go up one level from scripts)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_agents.round1.quiz_service import QuizService

def simulate_user_answer(question_data, correct_rate=0.7):
    """Simulate a user answering a question with some accuracy."""
    # Since we don't have the correct answer in the API response (for security),
    # we'll just randomly pick an answer with some intelligence based on topic difficulty
    options = ["A", "B", "C", "D"]
    
    # Simulate different user behaviors based on topic
    topic = question_data.get("topic", "")
    
    # Adjust probability based on topic complexity
    if topic in ["Formulas", "VBA", "Data Analysis"]:
        # Harder topics - lower accuracy
        actual_rate = correct_rate * 0.8
    elif topic in ["Shortcuts", "General", "Charts"]:
        # Easier topics - higher accuracy  
        actual_rate = correct_rate * 1.2
    else:
        actual_rate = correct_rate
    
    # Cap at reasonable bounds
    actual_rate = min(0.9, max(0.3, actual_rate))
    
    # For simulation purposes, we'll assume option C is often correct
    # (this is just for demo - real users would actually read and think)
    if random.random() < actual_rate:
        return random.choice(["B", "C"])  # Slightly favor B and C
    else:
        return random.choice(["A", "D"])  # Wrong answers

def print_question(question_data):
    """Pretty print a question."""
    print(f"\n📝 Question {question_data['question_number']}/{question_data['total_questions']}")
    print(f"🏷️  Topic: {question_data['topic']}")
    print(f"❓ {question_data['question']}")
    print()
    for letter, option in question_data['options'].items():
        print(f"   {letter}) {option}")
    print()

def print_answer_result(answer_data):
    """Pretty print answer result."""
    if answer_data['is_correct']:
        print(f"✅ Correct! You chose {answer_data['user_answer']}")
    else:
        print(f"❌ Incorrect. You chose {answer_data['user_answer']}, correct answer was {answer_data['correct_answer']}")
        print(f"   Correct option: {answer_data.get('correct_option', 'N/A')}")
    
    print(f"💡 {answer_data['explanation']}")
    
    if not answer_data['quiz_completed']:
        print(f"📊 Questions remaining: {answer_data.get('questions_remaining', 0)}")

def print_performance_catalog(performance_data):
    """Pretty print the final performance catalog."""
    print("\n" + "="*60)
    print("🎯 ROUND 1 COMPLETE - USER STRENGTHS CATALOG")
    print("="*60)
    
    print(f"\n📊 OVERALL PERFORMANCE:")
    print(f"   Questions Answered: {performance_data['total_questions']}")
    print(f"   Correct Answers: {performance_data['correct_answers']}")
    print(f"   Incorrect Answers: {performance_data['incorrect_answers']}")
    print(f"   Accuracy: {performance_data['accuracy']:.1%}")
    print(f"   Topics Explored: {performance_data['topics_attempted']}")
    
    print(f"\n✅ STRONG TOPICS ({len(performance_data['solved_topics'])} topics):")
    if performance_data['solved_topics']:
        for i, topic in enumerate(performance_data['solved_topics'], 1):
            print(f"   {i}. {topic}")
    else:
        print("   None identified yet - keep practicing!")
    
    print(f"\n❌ TOPICS TO REVIEW ({len(performance_data['unsolved_topics'])} topics):")
    if performance_data['unsolved_topics']:
        for i, topic in enumerate(performance_data['unsolved_topics'], 1):
            print(f"   {i}. {topic}")
    else:
        print("   Great job! No weak areas identified.")
    
    print(f"\n📈 DETAILED TOPIC BREAKDOWN:")
    for topic, stats in performance_data['topic_breakdown'].items():
        accuracy = stats['accuracy']
        status = stats['status'].upper()
        print(f"   📚 {topic:<20} {stats['correct']}/{stats['total']} ({accuracy:.1%}) - {status}")
    
    return performance_data

def simulate_complete_session():
    """Simulate a complete Round 1 quiz session."""
    print("🚀 STARTING ROUND 1 QUIZ SIMULATION")
    print("="*50)
    
    # Initialize quiz service
    quiz_service = QuizService()
    
    # Start quiz session
    print("🎬 Starting quiz session...")
    start_result = quiz_service.start_quiz_session(max_questions=12)
    
    if not start_result["success"]:
        print(f"❌ Failed to start quiz: {start_result['message']}")
        return
    
    print(f"✅ Quiz started successfully!")
    print(f"📊 {start_result['data']['available_questions']} questions available")
    print(f"🎯 Target: {start_result['data']['max_questions']} questions")
    
    # Simulate answering questions
    question_count = 0
    user_accuracy = 0.65  # Simulate 65% accuracy
    
    while True:
        # Get next question
        question_result = quiz_service.get_next_question()
        
        if not question_result["success"]:
            print(f"⚠️  No more questions: {question_result['message']}")
            break
        
        question_data = question_result["data"]
        print_question(question_data)
        
        # Simulate user thinking time
        time.sleep(0.5)
        
        # Simulate user answer
        user_answer = simulate_user_answer(question_data, user_accuracy)
        print(f"👤 User answers: {user_answer}")
        
        # Submit answer
        answer_result = quiz_service.submit_answer(user_answer)
        
        if not answer_result["success"]:
            print(f"❌ Failed to submit answer: {answer_result['message']}")
            break
        
        answer_data = answer_result["data"]
        print_answer_result(answer_data)
        
        question_count += 1
        
        # Check if quiz is completed
        if answer_data.get("quiz_completed", False):
            print(f"\n🎉 Quiz completed after {question_count} questions!")
            
            # Show final results if included
            if "final_results" in answer_data:
                final_performance = print_performance_catalog(answer_data["final_results"])
                
                # Show recommendations
                if "recommendations" in answer_data.get("final_results", {}):
                    recommendations = answer_data["final_results"]["recommendations"]
                    print(f"\n🎯 RECOMMENDATIONS:")
                    print(f"   Overall Performance: {recommendations.get('overall_performance', 'N/A').title()}")
                    
                    if recommendations.get('next_steps'):
                        print(f"   Next Steps:")
                        for step in recommendations['next_steps']:
                            print(f"   • {step}")
            
            break
        
        print(f"\n{'─'*50}")
    
    # Get final performance if not already shown
    if question_count > 0:
        final_result = quiz_service.get_current_performance()
        if final_result["success"]:
            print(f"\n🏁 FINAL SESSION SUMMARY:")
            print_performance_catalog(final_result["data"])
    
    print(f"\n🎊 ROUND 1 SIMULATION COMPLETE!")
    print(f"📈 The user's strengths and weaknesses have been cataloged.")
    print(f"🚀 Ready for Round 2 or targeted practice!")

def main():
    """Main simulation function."""
    try:
        simulate_complete_session()
    except KeyboardInterrupt:
        print(f"\n⏹️  Simulation interrupted by user")
    except Exception as e:
        print(f"\n💥 Simulation error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
