"""
LangGraph Quiz Agent with 5 nodes for adaptive quiz system.
"""
from langgraph.graph import StateGraph, END
from typing import Dict, Any
import random

from .agent_state import AgentState, create_initial_state
from .tools import (
    get_all_topics, get_question_by_topic_and_difficulty, 
    record_user_response, get_session_responses, get_session_performance,
    get_random_topic_from_list, filter_unasked_topics
)
from .groq_client import groq_client
from .question_generator import question_generator
from .user_summary_service import user_summary_service

class QuizAgent:
    """LangGraph-based adaptive quiz agent."""
    
    def __init__(self):
        self.graph = self._create_graph()
    
    def _create_graph(self) -> StateGraph:
        """Create the LangGraph state graph."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("node_1_initial_shortcuts", self.node_1_initial_shortcuts)
        workflow.add_node("node_2_check_response", self.node_2_check_response)
        workflow.add_node("node_3a_correct_followup", self.node_3a_correct_followup)
        workflow.add_node("node_3b_topic_catalog", self.node_3b_topic_catalog)
        workflow.add_node("node_4_select_new_topic", self.node_4_select_new_topic)
        workflow.add_node("node_5_ask_question", self.node_5_ask_question)
        workflow.add_node("node_6_generate_questions_and_summary", self.node_6_generate_questions_and_summary)
        
        # Set entry point
        workflow.set_entry_point("node_1_initial_shortcuts")
        
        # Add edges
        workflow.add_edge("node_1_initial_shortcuts", "node_2_check_response")
        workflow.add_conditional_edges(
            "node_2_check_response",
            self.decide_after_check,
            {
                "correct": "node_3a_correct_followup",
                "incorrect": "node_3b_topic_catalog",
                "complete": "node_6_generate_questions_and_summary"
            }
        )
        workflow.add_edge("node_3a_correct_followup", "node_3b_topic_catalog")
        workflow.add_edge("node_3b_topic_catalog", "node_4_select_new_topic")
        workflow.add_conditional_edges(
            "node_4_select_new_topic",
            self.decide_after_topic_selection,
            {
                "continue": "node_5_ask_question",
                "complete": "node_6_generate_questions_and_summary"
            }
        )
        workflow.add_conditional_edges(
            "node_5_ask_question",
            self.decide_after_question,
            {
                "correct": "node_3a_correct_followup",
                "incorrect": "node_3b_topic_catalog",
                "complete": "node_6_generate_questions_and_summary"
            }
        )
        
        # Node 6 is the final node
        workflow.add_edge("node_6_generate_questions_and_summary", END)
        
        return workflow.compile()
    
    def node_1_initial_shortcuts(self, state: AgentState) -> Dict[str, Any]:
        """Node 1: Static node - ask initial shortcuts question (easy difficulty)."""
        print("🚀 Starting quiz with shortcuts question...")
        
        # Get a shortcuts question with easy difficulty
        question = get_question_by_topic_and_difficulty("Shortcuts", "easy")
        
        if not question:
            print("❌ No shortcuts questions found!")
            state["is_complete"] = True
            return state
        
        # Present question to user using Groq (don't expose correct answer)
        question_for_ai = {
            "question": question["question"],
            "options": question["options"],
            "topic": question["topic"],
            "difficulty": question["difficulty"]
        }
        ai_question = groq_client.ask_question_to_user(question_for_ai)
        print(f"\n🤖 AI: {ai_question}")
        
        # Get user input (in real implementation, this would be from UI)
        user_answer = input("\nYour answer (A, B, C, or D): ").strip().upper()
        
        # Record the response
        record_result = record_user_response(
            session_id=state["session_id"],
            question_id=question["question_id"],
            user_answer=user_answer,
            additional_data={"node": "node_1_initial_shortcuts"}
        )
        
        # Update state
        state["current_question"] = question
        state["current_response"] = user_answer
        state["questions_asked"] += 1
        state["current_topic"] = "Shortcuts"
        state["topics_asked"].append("Shortcuts")
        state["node_history"].append("node_1_initial_shortcuts")
        
        if record_result.get("success"):
            state["last_answer_correct"] = record_result["is_correct"]
            
            # Provide feedback
            feedback = groq_client.provide_feedback(
                is_correct=record_result["is_correct"],
                correct_answer=record_result["correct_answer"],
                topic="Shortcuts"
            )
            print(f"\n🤖 Feedback: {feedback}")
        else:
            print(f"❌ Failed to record response: {record_result}")
            # Fallback - calculate correctness locally
            is_correct = user_answer == question["correct_answer"]
            state["last_answer_correct"] = is_correct
        
        return state
    
    def node_2_check_response(self, state: AgentState) -> Dict[str, Any]:
        """Node 2: Check if user got the last question correct."""
        print("🔍 Checking your response...")
        
        # Get the latest response from database
        responses = get_session_responses(state["session_id"])
        if responses:
            latest_response = responses[-1]
            state["last_answer_correct"] = latest_response["is_correct"]
            print(f"✅ Last answer was: {'Correct' if latest_response['is_correct'] else 'Incorrect'}")
        
        state["node_history"].append("node_2_check_response")
        return state
    
    def node_3a_correct_followup(self, state: AgentState) -> Dict[str, Any]:
        """Node 3A: Ask 2 easy + 2 medium questions on the same topic."""
        print(f"🎯 Great job! Let's explore {state['current_topic']} further...")
        
        current_topic = state["current_topic"]
        
        # Ask 2 easy questions
        for i in range(2):
            if state["questions_asked"] >= state["total_questions_limit"]:
                break
                
            question = get_question_by_topic_and_difficulty(current_topic, "easy")
            if question:
                # Don't expose correct answer to AI
                question_for_ai = {
                    "question": question["question"],
                    "options": question["options"],
                    "topic": question["topic"],
                    "difficulty": question["difficulty"]
                }
                ai_question = groq_client.ask_question_to_user(question_for_ai)
                print(f"\n🤖 Easy Question {i+1}: {ai_question}")
                
                user_answer = input("\nYour answer (A, B, C, or D): ").strip().upper()
                
                record_result = record_user_response(
                    session_id=state["session_id"],
                    question_id=question["question_id"],
                    user_answer=user_answer,
                    additional_data={"node": "node_3a_correct_followup", "question_type": "easy_followup"}
                )
                
                state["questions_asked"] += 1
                
                if record_result.get("success"):
                    feedback = groq_client.provide_feedback(
                        is_correct=record_result["is_correct"],
                        correct_answer=record_result["correct_answer"],
                        topic=current_topic
                    )
                    print(f"\n🤖 Feedback: {feedback}")
        
        # Ask 2 medium questions
        for i in range(2):
            if state["questions_asked"] >= state["total_questions_limit"]:
                break
                
            question = get_question_by_topic_and_difficulty(current_topic, "medium")
            if question:
                # Don't expose correct answer to AI
                question_for_ai = {
                    "question": question["question"],
                    "options": question["options"],
                    "topic": question["topic"],
                    "difficulty": question["difficulty"]
                }
                ai_question = groq_client.ask_question_to_user(question_for_ai)
                print(f"\n🤖 Medium Question {i+1}: {ai_question}")
                
                user_answer = input("\nYour answer (A, B, C, or D): ").strip().upper()
                
                record_result = record_user_response(
                    session_id=state["session_id"],
                    question_id=question["question_id"],
                    user_answer=user_answer,
                    additional_data={"node": "node_3a_correct_followup", "question_type": "medium_followup"}
                )
                
                state["questions_asked"] += 1
                
                if record_result.get("success"):
                    feedback = groq_client.provide_feedback(
                        is_correct=record_result["is_correct"],
                        correct_answer=record_result["correct_answer"],
                        topic=current_topic
                    )
                    print(f"\n🤖 Feedback: {feedback}")
        
        state["node_history"].append("node_3a_correct_followup")
        return state
    
    def node_3b_topic_catalog(self, state: AgentState) -> Dict[str, Any]:
        """Node 3B: Get catalog of all topics and filter unasked ones."""
        print("📚 Analyzing topic catalog...")
        
        # Get all available topics
        if not state["all_topics"]:
            state["all_topics"] = get_all_topics()
        
        # Filter out topics that have been asked
        unasked_topics = filter_unasked_topics(state["all_topics"], state["topics_asked"])
        
        print(f"📊 Total topics: {len(state['all_topics'])}")
        print(f"🎯 Topics covered: {len(state['topics_asked'])}")
        print(f"📝 Remaining topics: {len(unasked_topics)}")
        
        state["node_history"].append("node_3b_topic_catalog")
        return state
    
    def node_4_select_new_topic(self, state: AgentState) -> Dict[str, Any]:
        """Node 4: Select a random topic from unasked topics."""
        print("🎲 Selecting new topic...")
        
        unasked_topics = filter_unasked_topics(state["all_topics"], state["topics_asked"])
        
        if not unasked_topics:
            print("🎉 All topics have been covered!")
            state["is_complete"] = True
            return state
        
        # Randomly choose a topic
        new_topic = get_random_topic_from_list(unasked_topics)
        state["current_topic"] = new_topic
        
        print(f"📌 Selected topic: {new_topic}")
        
        state["node_history"].append("node_4_select_new_topic")
        return state
    
    def node_5_ask_question(self, state: AgentState) -> Dict[str, Any]:
        """Node 5: Ask a question with selected topic and easy difficulty."""
        print(f"❓ Asking question about {state['current_topic']}...")
        
        question = get_question_by_topic_and_difficulty(state["current_topic"], "easy")
        
        if not question:
            print(f"❌ No questions found for topic: {state['current_topic']}")
            # Try to get another topic
            unasked_topics = filter_unasked_topics(state["all_topics"], state["topics_asked"])
            if unasked_topics:
                state["current_topic"] = get_random_topic_from_list(unasked_topics)
                question = get_question_by_topic_and_difficulty(state["current_topic"], "easy")
        
        if not question:
            print("❌ No more questions available!")
            state["is_complete"] = True
            return state
        
        # Present question to user (don't expose correct answer)
        question_for_ai = {
            "question": question["question"],
            "options": question["options"],
            "topic": question["topic"],
            "difficulty": question["difficulty"]
        }
        ai_question = groq_client.ask_question_to_user(question_for_ai)
        print(f"\n🤖 AI: {ai_question}")
        
        user_answer = input("\nYour answer (A, B, C, or D): ").strip().upper()
        
        # Record the response
        record_result = record_user_response(
            session_id=state["session_id"],
            question_id=question["question_id"],
            user_answer=user_answer,
            additional_data={"node": "node_5_ask_question"}
        )
        
        # Update state
        state["current_question"] = question
        state["current_response"] = user_answer
        state["questions_asked"] += 1
        
        # Add topic to asked topics if not already there
        if state["current_topic"] not in state["topics_asked"]:
            state["topics_asked"].append(state["current_topic"])
        
        if record_result.get("success"):
            state["last_answer_correct"] = record_result["is_correct"]
            
            feedback = groq_client.provide_feedback(
                is_correct=record_result["is_correct"],
                correct_answer=record_result["correct_answer"],
                topic=state["current_topic"]
            )
            print(f"\n🤖 Feedback: {feedback}")
        
        state["node_history"].append("node_5_ask_question")
        return state
    
    def node_6_generate_questions_and_summary(self, state: AgentState) -> Dict[str, Any]:
        """Node 6: Generate new questions and comprehensive user summary."""
        print("\n" + "=" * 60)
        print("🔬 ASSESSMENT COMPLETE - ANALYZING PERFORMANCE...")
        print("=" * 60)
        
        # Get all session responses
        session_responses = get_session_responses(state["session_id"])
        
        # Generate and save user summary
        print("📋 Generating comprehensive user summary...")
        summary_result = user_summary_service.save_user_summary(state, session_responses)
        
        if summary_result["success"]:
            print(f"✅ User summary saved successfully (ID: {summary_result['summary_id']})")
            state["user_summary"] = summary_result["ai_summary"]
        else:
            print(f"❌ Failed to save user summary: {summary_result['message']}")
        
        # Generate new questions to improve the questionnaire
        print("\n🧠 IMPROVING QUESTIONNAIRE...")
        print("Generating 5 new questions based on your performance...")
        
        generation_result = question_generator.generate_and_save_questions(
            session_responses, 
            count=5
        )
        
        if generation_result["success"]:
            print(f"✅ Generated and saved {generation_result['saved_count']} new questions!")
            print("📈 The questionnaire has been improved for future users!")
            
            # Display generated questions summary
            if generation_result.get("generated_questions"):
                print("\n📝 New questions added to database:")
                for i, q in enumerate(generation_result["generated_questions"], 1):
                    print(f"   {i}. {q['topic']} ({q['difficulty']}): {q['question'][:60]}...")
        else:
            print(f"❌ Failed to generate new questions: {generation_result['message']}")
        
        # Store results in state
        state["question_generation_result"] = generation_result
        state["user_summary_result"] = summary_result
        state["node_history"].append("node_6_generate_questions_and_summary")
        state["is_complete"] = True
        
        print("\n🎯 Assessment and improvement cycle complete!")
        return state
    
    def decide_after_check(self, state: AgentState) -> str:
        """Decide next node after checking response."""
        if state["questions_asked"] >= state["total_questions_limit"]:
            return "complete"
        
        if state["last_answer_correct"]:
            return "correct"
        else:
            return "incorrect"
    
    def decide_after_topic_selection(self, state: AgentState) -> str:
        """Decide next node after topic selection."""
        if state["questions_asked"] >= state["total_questions_limit"] or state["is_complete"]:
            return "complete"
        return "continue"
    
    def decide_after_question(self, state: AgentState) -> str:
        """Decide next node after asking a question."""
        if state["questions_asked"] >= state["total_questions_limit"]:
            return "complete"
        
        if state["last_answer_correct"]:
            return "correct"
        else:
            return "incorrect"
    
    def run_quiz(self, user_id: str = None) -> Dict[str, Any]:
        """Run the complete quiz session."""
        print("🎓 Welcome to the Adaptive Quiz System!")
        print("=" * 50)
        
        # Create initial state
        initial_state = create_initial_state(user_id)
        
        # Run the graph
        final_state = self.graph.invoke(initial_state)
        
        # Generate performance summary
        print("\n" + "=" * 50)
        print("📊 Generating Performance Summary...")
        
        performance_data = get_session_performance(final_state["session_id"])
        if performance_data:
            summary = groq_client.generate_performance_summary(performance_data)
            print(f"\n🤖 Performance Summary:\n{summary}")
            final_state["performance_summary"] = performance_data
        
        print(f"\n🎯 Quiz completed! Total questions answered: {final_state['questions_asked']}")
        print(f"📝 Session ID: {final_state['session_id']}")
        
        return final_state

# Create global agent instance
quiz_agent = QuizAgent()
